import urllib.request
import datetime
import pandas as pd
import sys
from bs4 import BeautifulSoup
from lxml import html
import re
import urllib.parse
import traceback  # for better error logging

def is_valid_post(row):
    """
    게시글이 유효한지 판단하는 함수 (green 링크 포함 여부 검사)
    """
    title_link = row.select_one('td.listsubject a')
    if not title_link or not title_link.has_attr('href'):
        return False
    return 'green=' not in title_link['href']

def parse_post_time(raw_time: str, year: int) -> pd.Timestamp:
    full_time = f"{year}.{raw_time}"
    try:
        return pd.to_datetime(full_time, format="%Y.%m.%d %H:%M")
    except ValueError:
        return pd.to_datetime(full_time, format="%Y.%m.%d")

def get_instiz_keyword_data(keyword: str, starttime: str, endtime: str) -> pd.DataFrame:
    title, time_list, contents, url_list = [], [], [], []
    view, like, comment, cate, search_keyword = [], [], [], [], []

    base_url = "https://www.instiz.net"
    encoded_keyword = urllib.parse.quote(keyword, safe='')
    now_year = datetime.datetime.now().year
    today = pd.to_datetime(datetime.datetime.now().strftime('%Y.%m.%d'))

    for page in range(1, 100):
        try:
            full_url = (
                f"{base_url}/name?page={page}&category=1"
                f"&k={encoded_keyword}&stype=9&starttime={starttime}&endtime={endtime}"
            )
            print(f"[DEBUG] 🔍 검색 URL(Page {page}): {full_url}")

            response = urllib.request.urlopen(full_url)
            soup = BeautifulSoup(response.read().decode('utf-8'), 'html.parser')
            all_rows = soup.select('tr#detour')

            # ✅ 'green=' 이 포함된 링크 필터링
            filtered_rows = [row for row in all_rows if is_valid_post(row)]

            if not filtered_rows:
                print(f"[INFO] Page {page} - 유효 게시글 없음, 크롤링 종료")
                break

            for row in filtered_rows:
                title_link = row.select_one('td.listsubject a')
                post_url = base_url + title_link['href'].replace('..', '')
                titlestr = title_link.get_text(strip=True)

                time_cell = row.select_one('td.listno.regdate')
                timestr = time_cell.get_text(strip=True) if time_cell else ''
                parsed_time = parse_post_time(timestr, now_year) if timestr else today

                stat_cells = row.select('td.listno')
                view_count = stat_cells[-2].get_text(strip=True) if len(stat_cells) >= 3 else ''
                like_count = stat_cells[-1].get_text(strip=True) if len(stat_cells) >= 3 else ''
                comment_count = row.select_one('span.cmt2')
                comment_text = comment_count.get_text(strip=True) if comment_count else '0'

                # 본문 크롤링
                try:
                    post_resp = urllib.request.urlopen(post_url)
                    post_html = post_resp.read()
                    doc = html.fromstring(post_html)

                    content_div = doc.get_element_by_id('memo_content_1')
                    for tag in content_div.xpath('.//script | .//style | .//img'):
                        tag.getparent().remove(tag)

                    raw_text = content_div.text_content()
                    clean_text = re.sub(r'\s+', ' ', raw_text).strip()

                except Exception as e:
                    print(f"[ERROR] 본문 크롤링 실패 ({post_url}): {e}", file=sys.stderr)
                    traceback.print_exc()
                    clean_text = ''

                # 데이터 추가
                title.append(titlestr)
                url_list.append(post_url)
                time_list.append(parsed_time)
                view.append(view_count)
                like.append(like_count)
                comment.append(comment_text)
                cate.append('instiz')
                search_keyword.append(keyword)
                contents.append(clean_text)

        except Exception as e:
            print(f"[ERROR] Page {page}에서 오류 발생: {e}", file=sys.stderr)
            traceback.print_exc()
            continue

    df = pd.DataFrame({
        'title': title,
        'time': time_list,
        'contents': contents,
        'url': url_list,
        'view': view,
        'like': like,
        'comment': comment,
        'cate': cate,
        'keyword': search_keyword,
    })

    print(f"[✓] 총 {len(df)}개 게시글 크롤링 완료")
    return df

def save_df_to_csv(save_path: str, df: pd.DataFrame) -> None:
    """
    DataFrame을 CSV 파일로 저장하는 함수
    """
    try:
        df.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"[✓] 데이터 저장 완료: {save_path}")
    except Exception as e:
        print(f"[ERROR] 데이터 저장 실패: {e}", file=sys.stderr)
        traceback.print_exc()

def data_processing(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrame을 처리하는 함수 (필요시 추가)
    """
    #contents열의 시작이 죄송해요로 시작하는 행을 삭제
    ret_df = df[~df['contents'].str.startswith('죄송해요,')]
    
    # title과 contents를 contents로 합치기
    ret_df['contents'] = ret_df['title'] + ' ' + ret_df['contents']
    ret_df.drop(columns=['title'], inplace=True)
    
    return ret_df


if __name__ == "__main__":
    save_path = 'data/instiz_keyword_data.csv'
    df = get_instiz_keyword_data(keyword='수건케이크', starttime='20241010', endtime='20250310')
    print("[INFO] 크롤링한 데이터 처리 중...")
    processed_df = data_processing(df)
    save_df_to_csv(save_path, processed_df)
    print("[INFO] 크롤링 및 저장 완료")