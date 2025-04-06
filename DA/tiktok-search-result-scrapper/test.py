import time
import csv
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 설정값
TARGET_URL = "https://www.google.com/search?q=%EB%B0%A4%ED%8B%B0%EB%9D%BC%EB%AF%B8%EC%88%98+tiktok&num=12&udm=39"
MAX_ITEMS = 100
WAIT = 2
OUTPUT_PATH = "tiktok_video_ids_with_titles.csv"

# Chrome 옵션 설정
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

# WebDriver 실행
driver = webdriver.Chrome(options=options)
driver.get(TARGET_URL)
time.sleep(WAIT)

results = []
scroll_count = 0

def click_more_results_if_available():
    try:
        more_button = driver.find_element(By.XPATH, '//span[text()="결과 더보기" or text()="More results"]')
        driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
        time.sleep(1)
        more_button.click()
        print("🔁 '결과 더보기' 버튼 클릭")
        return True
    except:
        return False

while len(results) < MAX_ITEMS and scroll_count < 30:
    print(f"🔍 스크롤 {scroll_count + 1}회차 | 현재 수집: {len(results)}개")

    link_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "tiktok.com/") and contains(@href, "/video/")]')

    for link_el in link_elements:
        try:
            url = link_el.get_attribute("href")
            match = re.search(r'/video/(\d+)', url)
            if not match:
                continue
            video_id = match.group(1)

            # 한 단계 위 부모 div에서 제목 찾기
            try:
                heading_div = link_el.find_element(By.XPATH, '..')
                title = heading_div.get_attribute("aria-label") or heading_div.text.strip()
            except:
                title = ""

            # 중복 방지
            if not any(item['video_id'] == video_id for item in results):
                results.append({
                    'video_id': video_id,
                    'url': url,
                    'title': title
                })

            if len(results) >= MAX_ITEMS:
                break

        except Exception as e:
            print(f"⚠️ 링크 처리 중 오류: {e}")
            continue

    # 더보기 or 스크롤
    if not click_more_results_if_available():
        driver.execute_script("window.scrollBy(0, 1000)")
        time.sleep(WAIT)

    scroll_count += 1
    time.sleep(WAIT)

driver.quit()

# 결과 저장
with open(OUTPUT_PATH, "w", newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=["video_id", "url", "title"])
    writer.writeheader()
    for item in results:
        writer.writerow(item)

print(f"\n✅ 완료: 총 {len(results)}개의 TikTok 영상 정보가 저장되었습니다 → {OUTPUT_PATH}")
