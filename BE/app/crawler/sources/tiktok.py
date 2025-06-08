# 여기에 틱톡 크롤러 코드 작성

import time
import re
import emoji
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from .tiktokcomment import TiktokComment
from .tiktokcomment.typing import Comments, Comment
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models import Keywords

class TikTokCrawler:
    def __init__(self):
        # 현재는 초기화할 값이 없습니다.
        pass

    def _is_valid_korean_content(self, text: str) -> bool:
        _emoji_pattern = emoji.get_emoji_regexp()

        if any(kw in text for kw in ("레시피", "만들기")):
            return False
        if re.search(r"https?://\S+", text):
            return False
        if not re.search(r"[가-힣]", text):
            return False
        return True

    async def crawl(self, keyword: Keywords, start_date: str, end_date: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        TikTok 영상 및 댓글을 함께 크롤링합니다.
        :return: {
            "videos": [video_dict, ...],
            "comments": [comment_dict, ...]
        }
        """
        query = f'{keyword.keyword}+tiktok+after%3A{start_date}+before%3A{end_date}'
        target_url = f"https://www.google.com/search?q={query}&num=12&udm=39"

        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

        driver = webdriver.Chrome(options=options)
        driver.get(target_url)
        time.sleep(2)

        videos = []
        all_comments = []

        scroll_count = 0
        MAX_ITEMS = 50
        WAIT = 2

        def click_more_results_if_available():
            try:
                more_button = driver.find_element(By.XPATH, '//span[text()="결과 더보기" or text()="More results"]')
                driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
                time.sleep(1)
                more_button.click()
                return True
            except:
                return False

        while len(videos) < MAX_ITEMS and scroll_count < 30:
            link_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "tiktok.com/") and contains(@href, "/video/")]')
            for link_el in link_elements:
                try:
                    url = link_el.get_attribute("href")
                    match = re.search(r'/video/(\d+)', url)
                    if not match:
                        continue
                    video_id = match.group(1)
                    try:
                        heading_div = link_el.find_element(By.XPATH, '..')
                        title = heading_div.get_attribute("aria-label") or heading_div.text.strip()
                    except:
                        title = ""
                    if not title or not self._is_valid_korean_content(title):
                        continue

                    if not any(item['id'] == video_id for item in videos):
                        collected_time = datetime.now()

                        video = {
                            'id': video_id,
                            'title': title,
                            'video_url': url,
                            'keyword_id': keyword.id,
                            'collected_at': collected_time
                        }
                        videos.append(video)

                        # ✅ 댓글 수집
                        print(f"[LOG] 댓글 수집 중: {video_id}")
                        comments = await self.crawl_comments(video_id, keyword.id)
                        all_comments.extend(comments)

                    if len(videos) >= MAX_ITEMS:
                        break
                except Exception:
                    continue
            if not click_more_results_if_available():
                driver.execute_script("window.scrollBy(0, 1000)")
                time.sleep(WAIT)
            scroll_count += 1
            time.sleep(WAIT)

        driver.quit()

        return {
            "videos": videos,
            "comments": all_comments
        }


    async def crawl_comments(self, video_id: str, keyword_id: int) -> List[Dict[str, Any]]:
        """
        특정 TikTok 비디오의 댓글 및 답글을 크롤링하여 TiktokComments 모델에 맞는 dict 리스트로 반환합니다.
        :param video_id: TikTok 비디오 ID
        :return: 각 댓글/답글에 대해 TiktokComments 모델 dict의 리스트
        (id, video_id, text, reply_count, user_id, nickname, parent_comment_id, is_reply, created_at)
        """
        scraper = TiktokComment()
        results = []

        def format_time(ts) -> Optional[datetime]:
            try:
                if isinstance(ts, (int, float)) or (isinstance(ts, str) and ts.isdigit()):
                    return datetime.fromtimestamp(int(ts))
                elif isinstance(ts, str) and 'T' in ts:
                    return datetime.fromisoformat(ts)
            except Exception:
                return None

        try:
            comments_obj: Comments = scraper(aweme_id=video_id)
            for comment in comments_obj.comments:
                if not self._is_valid_korean_content(comment.comment):
                    continue
                results.append({
                    "id": comment.comment_id,
                    "video_id": video_id,
                    "keyword_id": keyword_id, 
                    "content": comment.comment,
                    "reply_count": comment.total_reply,
                    "user_id": comment.username,
                    "nickname": comment.nickname,
                    "parent_comment_id": None,
                    "is_reply": False,
                    "created_at": format_time(comment.create_time),
                    "collected_at": datetime.now()
                })
                for reply in comment.replies:
                    results.append({
                        "id": reply.comment_id,
                        "video_id": video_id,
                        "keyword_id": keyword_id,
                        "content": reply.comment,
                        "reply_count": reply.total_reply,
                        "user_id": reply.username,
                        "nickname": reply.nickname,
                        "parent_comment_id": comment.comment_id,
                        "is_reply": True,
                        "created_at": format_time(reply.create_time),
                        "collected_at": datetime.now()
                    })
        except Exception:
            pass

        return results
