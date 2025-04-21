#!/usr/bin/env python
import time
import json
import os
import csv
from tqdm import tqdm
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from collections import OrderedDict
from googleapiclient.discovery import build

API_KEY = None
YOUTUBE = None
# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

# ======= 유틸 =======

def convert_to_rfc3339(date_str, is_start=True):
    return f"{date_str}T00:00:00Z" if is_start else f"{date_str}T23:59:59Z"

def dedup_video_list(videos):
    return list(OrderedDict((v["videoId"], v) for v in videos).values())

def save_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"✅ CSV 저장 완료: {filename}")

# ======= API 호출 =======

def search_videos(keyword, start_rfc, end_rfc, duration=None):
    videos = []
    page_token = None
    while True:
        request = YOUTUBE.search().list(
            part="snippet",
            q=keyword,
            type="video",
            publishedAfter=start_rfc,
            publishedBefore=end_rfc,
            videoDuration=duration,
            maxResults=50,
            pageToken=page_token
        )
        response = request.execute()
        for item in response.get("items", []):
            videos.append({
                "videoId": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "publishedAt": item["snippet"]["publishedAt"]
            })
        page_token = response.get("nextPageToken")
        if not page_token:
            break
    return videos

def get_video_details(video_ids):
    details = []
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        request = YOUTUBE.videos().list(
            part="snippet,statistics",
            id=",".join(batch_ids),
            maxResults=50
        )
        response = request.execute()
        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            details.append({
                "videoId": item["id"],
                "title": snippet.get("title", ""),
                "publishedAt": snippet.get("publishedAt", ""),
                "likeCount": stats.get("likeCount", ""),
                "commentCount": stats.get("commentCount", ""),
                "viewCount": stats.get("viewCount", ""),
                "channelId": snippet.get("channelId", "")
            })
    return details

def get_comments_threadsafe(video_id, max_comments=300):
    youtube = build("youtube", "v3", developerKey=API_KEY)  # 각 스레드마다 생성
    comments_info = []
    page_token = None

    while True:
        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=page_token,
                textFormat="plainText"
            )
            response = request.execute()
        except Exception as e:
            print(f"❌ 댓글 수집 실패 [{video_id}]: {e}")
            break

        for item in response.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments_info.append({
                "날짜": snippet["publishedAt"],
                "video_id": video_id,
                "comment_id": item["snippet"]["topLevelComment"]["id"],
                "comment_text": snippet["textDisplay"]
            })
            if len(comments_info) >= max_comments:
                return comments_info

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return comments_info

def fetch_comments_parallel(video_ids, max_comments_per_video=300, max_workers=4):
    comments_all = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(get_comments_threadsafe, vid, max_comments_per_video) for vid in video_ids]
        for future in tqdm(futures, desc="댓글 병렬 수집", unit="video"):
            try:
                comments_all.extend(future.result())
            except Exception as e:
                print("❌ 댓글 수집 실패 (병렬 처리):", e)
    return comments_all

# ======= MAIN =======

def main():
    global API_KEY, YOUTUBE


    # 사용자 입력
    keyword = input("검색 키워드: ").strip()
    start_date = input("시작 날짜 (YYYY-MM-DD): ").strip()
    end_date = input("종료 날짜 (YYYY-MM-DD): ").strip()
    API_KEY = input("유튜브 API 키: ").strip()
    YOUTUBE = build("youtube", "v3", developerKey=API_KEY)

    start_rfc = convert_to_rfc3339(start_date, True)
    end_rfc = convert_to_rfc3339(end_date, False)

    overall_start = time.time()  # ✅ 전체 실행 시간 측정 시작

    cache_file = f"search_cache_{keyword}_{start_date}_{end_date}.json"

    if os.path.exists(cache_file):
        print("✅ 캐시된 검색 결과 불러오는 중...")
        with open(cache_file, "r", encoding="utf-8") as f:
            videos_for_meta = json.load(f)
    else:
        print("🔍 롱폼/숏폼 영상 검색 중...")

        videos_longform = search_videos(keyword, start_rfc, end_rfc, duration="long")
        for v in videos_longform:
            v["duration_type"] = "long"

        videos_shorts = search_videos(keyword, start_rfc, end_rfc, duration="short")
        for v in videos_shorts:
            v["duration_type"] = "short"

        # 합치고 중복 제거
        videos_combined = dedup_video_list(videos_longform + videos_shorts)

        # 저장용 캐시
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(videos_combined, f, indent=2, ensure_ascii=False)

        videos_for_meta = videos_combined

        print(f"✅ 검색된 영상 수 (롱+숏): {len(videos_for_meta)}개")
        search_end = time.time()  # ✅ 검색 시간 측정 종료
        print(f"\n검색 시간: {search_end - overall_start:.2f}초\n")


    video_ids = [v["videoId"] for v in videos_for_meta]
    if not video_ids:
        print("❌ 검색된 영상이 없습니다.")
        return

    print("📊 영상 통계 정보 수집 중...")
    video_details = get_video_details(video_ids)
    save_csv(video_details, f"{keyword}_metadata_{start_date}_{end_date}.csv")
    print(f"✅ 메타데이터 수집 완료: {len(video_details)}개")
    details_end = time.time()  # ✅ 메타데이터 수집 시간 측정 종료
    print(f"\n메타데이터 수집 시간: {details_end - search_end:.2f}초\n")

    print("💬 댓글 수집 중 (병렬)...")
    comments = fetch_comments_parallel(video_ids, max_comments_per_video=300)
    save_csv(comments, f"{keyword}_comments_{start_date}_{end_date}.csv")
    print(f"✅ 댓글 수집 완료: {len(comments)}개")
    comments_end = time.time()  # ✅ 댓글 수집 시간 측정 종료
    print(f"\n댓글 수집 시간: {comments_end - details_end:.2f}초\n")

    print("✅ 모든 작업 완료.")
    overall_end = time.time()  # ✅ 전체 실행 시간 측정 종료
    print(f"\n전체 실행 시간: {overall_end - overall_start:.2f}초\n")

if __name__ == "__main__":
    main()
