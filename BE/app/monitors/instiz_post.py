import urllib.request
from bs4 import BeautifulSoup
from lxml import html

class InstizPostMonitor:
    def __init__(self):
        self.base_url = "https://www.instiz.net"

    def update_post_metrics(self, post_url: str) -> dict:
        """
        기존 post_url에 대해 실시간 지표(조회수, 좋아요, 댓글수)를 갱신해서 반환
        """
        try:
            response = urllib.request.urlopen(post_url)
            soup = BeautifulSoup(response.read().decode('utf-8'), 'html.parser')
            listnos = soup.select('td.listno')
            view = int(listnos[-2].get_text(strip=True).replace(',', '') if len(listnos) >= 3 else 0)
            like = int(listnos[-1].get_text(strip=True).replace(',', '') if len(listnos) >= 3 else 0)

            # 댓글 수는 본문 크롤링이 필요할 수도 있음
            doc = html.fromstring(response.read())
            comment_elements = doc.xpath('//div[@class="memo_list"]//div[contains(@id, "memo_list_")]')
            comment = len(comment_elements)

            return {
                "view_count": view,
                "like_count": like,
                "comment_count": comment
            }

        except Exception as e:
            print(f"Error updating {post_url}: {e}")
            return {}
