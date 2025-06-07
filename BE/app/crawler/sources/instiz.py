import urllib.request
import datetime
from bs4 import BeautifulSoup
from lxml import html
import re
import urllib.parse
import pandas as pd

from app.models import Keywords

class InstizCrawler:
    def __init__(self):
        # 현재는 초기화할 값이 없으나, 확장성을 위해 남겨둡니다.
        pass

    async def crawl(self, keyword: Keywords, starttime: str, endtime: str):
        """
        인스티즈 '익명잡담' 게시판에서 특정 키워드로 검색된 글들을 크롤링하여
        InstizPosts 모델에 저장하기 적합한 dict 리스트로 반환합니다.

        Parameters:
            keyword (Keywords): 키워드 모델 인스턴스 (keyword.id, keyword.keyword 사용)
            starttime (str): 검색 시작 날짜 (형식: YYYYMMDD)
            endtime (str): 검색 종료 날짜 (형식: YYYYMMDD)

        Returns:
            List[dict]: InstizPosts 테이블 저장용 데이터 리스트
        """
        results = []
        base_url = "https://www.instiz.net"
        encoded_keyword = urllib.parse.quote(keyword.keyword, safe='')
        start_date = datetime.datetime.strptime(starttime, "%Y%m%d")
        collected_time = datetime.datetime.utcnow()

        for page in range(1, 100):
            try:
                full_url = (
                    f'{base_url}/name?page={page}&category=1'
                    f'&k={encoded_keyword}&stype=9&starttime={starttime}&endtime={endtime}'
                )
                response = urllib.request.urlopen(full_url)
                soup = BeautifulSoup(response.read().decode('utf-8'), 'html.parser')
                rows = soup.select('tr#detour')
                if not rows:
                    break

                valid_post_found = False
                for row in rows:
                    title_cell = row.select_one('td.listsubject a')
                    if not title_cell or not title_cell.has_attr('href'):
                        continue
                    post_href = title_cell['href']
                    post_url = base_url + post_href.replace('..', '')

                    # green이 url에 포함된 경우 건너뜀
                    if 'green' in post_url:
                        continue

                    valid_post_found = True

                    # 날짜 파싱
                    time_cell = row.select_one('td.listno.regdate')
                    if time_cell:
                        timestr = time_cell.get_text(strip=True)  # 예: "10.30 23:58" 또는 "10.30"
                        try:
                            # 일단 현재 연도 기준으로 파싱
                            tmp_datetime = pd.to_datetime(f"{start_date.year}.{timestr}", format="%Y.%m.%d %H:%M", errors="coerce")
                            if tmp_datetime is None or pd.isna(tmp_datetime):
                                tmp_datetime = pd.to_datetime(f"{start_date.year}.{timestr}", format="%Y.%m.%d", errors="coerce")
                        except:
                            tmp_datetime = None

                        if tmp_datetime:
                            # 연도 보정: start_date 기준으로 가장 가까운 연도 선택
                            candidates = [
                                tmp_datetime.replace(year=start_date.year - 1),
                                tmp_datetime.replace(year=start_date.year),
                                tmp_datetime.replace(year=start_date.year + 1),
                            ]
                            parsed_time = min(candidates, key=lambda d: abs((d - start_date).days))
                        else:
                            parsed_time = start_date  # fallback
                    else:
                        parsed_time = start_date  # fallback

                    # 조회수, 추천수
                    listnos = row.select('td.listno')
                    view = int(listnos[-2].get_text(strip=True).replace(',', '') if len(listnos) >= 3 else 0)
                    like = int(listnos[-1].get_text(strip=True).replace(',', '') if len(listnos) >= 3 else 0)

                    # 댓글 수
                    comment_span = row.select_one('span.cmt2')
                    comment = int(comment_span.get_text(strip=True) if comment_span else 0)

                    # 본문 크롤링
                    try:
                        post_resp = urllib.request.urlopen(post_url)
                        post_html = post_resp.read()
                        doc = html.fromstring(post_html)
                        content_div = doc.get_element_by_id('memo_content_1')
                        for tag in content_div.xpath('.//script | .//style | .//img'):
                            tag.getparent().remove(tag)
                        text = content_div.text_content()
                        clean_body = re.sub(r'\s+', ' ', text).strip()
                    except Exception:
                        clean_body = ''

                    # ✅ '죄송해요,' 안내글 거르기
                    if clean_body.startswith("죄송해요,"):
                        continue

                    # ✅ 제목 + 본문 조합
                    title_text = title_cell.get_text(strip=True)
                    full_content = f"{title_text} {clean_body}".strip()



                    results.append({
                        "keyword_id": keyword.id,
                        "content": full_content,
                        "view_count": view,
                        "like_count": like,
                        "comment_count": comment,
                        "post_url": post_url,
                        "created_at": parsed_time,
                        "updated_at": parsed_time,
                        "collected_at": collected_time,
                    })

                if not valid_post_found:
                    break
            except Exception:
                continue

        return results
