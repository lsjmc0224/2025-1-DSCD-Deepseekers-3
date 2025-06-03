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
        now_year = datetime.datetime.now().year
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
                        timestr = time_cell.get_text(strip=True)
                        full_time = f"{now_year}.{timestr}"
                        try:
                            parsed_time = pd.to_datetime(full_time, format="%Y.%m.%d %H:%M")
                        except:
                            parsed_time = pd.to_datetime(full_time, format="%Y.%m.%d")
                    else:
                        parsed_time = datetime.datetime.now()

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
                        clean_text = re.sub(r'\s+', ' ', text).strip()
                    except Exception:
                        clean_text = ''

                    results.append({
                        "keyword_id": keyword.id,
                        "content": clean_text,
                        "view_count": view,
                        "like_count": like,
                        "comment_count": comment,
                        "post_url": post_url,
                        "created_at": parsed_time,
                        "updated_at": parsed_time,
                        "collected_at": collected_time,
                        # "is_analyzed": False → 저장 시점에서 처리
                    })

                if not valid_post_found:
                    break
            except Exception:
                continue

        return results
