# 여기에 틱톡 크롤러 코드 작성

import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from .tiktokcomment import TiktokComment
from .tiktokcomment.typing import Comments, Comment
from datetime import datetime
from typing import List, Dict, Any, Optional

class TikTokCrawler:
    def __init__(self):
        # 현재는 초기화할 값이 없습니다.
        pass

    async def crawl(self, keyword: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        구글 검색을 통해 TikTok 영상을 크롤링합니다.
        :param keyword: 검색 키워드
        :param start_date: 시작일 (YYYY-MM-DD)
        :param end_date: 종료일 (YYYY-MM-DD)
        :return: 각 영상에 대해 {id, title, video_url} dict의 리스트
        """
        # 구글 검색 쿼리 생성 (기간 필터 포함)
        query = f'{keyword}+tiktok+after%3A{start_date}+before%3A{end_date}'
        target_url = f"https://www.google.com/search?q={query}&num=12&udm=39"

        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

        driver = webdriver.Chrome(options=options)
        driver.get(target_url)
        time.sleep(2)

        results = []
        scroll_count = 0
        MAX_ITEMS = 100
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

        while len(results) < MAX_ITEMS and scroll_count < 30:
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
                    if not any(item['id'] == video_id for item in results):
                        results.append({
                            'id': video_id,
                            'title': title,
                            'video_url': url
                        })
                    if len(results) >= MAX_ITEMS:
                        break
                except Exception:
                    continue
            if not click_more_results_if_available():
                driver.execute_script("window.scrollBy(0, 1000)")
                time.sleep(WAIT)
            scroll_count += 1
            time.sleep(WAIT)
        driver.quit()
        return results

    async def crawl_comments(self, video_id: str) -> List[Dict[str, Any]]:
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
                results.append({
                    "id": comment.comment_id,
                    "video_id": video_id,
                    "text": comment.comment,
                    "reply_count": comment.total_reply,
                    "user_id": comment.username,
                    "nickname": comment.nickname,
                    "parent_comment_id": None,
                    "is_reply": False,
                    "created_at": format_time(comment.create_time)
                })
                for reply in comment.replies:
                    results.append({
                        "id": reply.comment_id,
                        "video_id": video_id,
                        "text": reply.comment,
                        "reply_count": reply.total_reply,
                        "user_id": reply.username,
                        "nickname": reply.nickname,
                        "parent_comment_id": comment.comment_id,
                        "is_reply": True,
                        "created_at": format_time(reply.create_time)
                    })
        except Exception:
            pass

        return results
