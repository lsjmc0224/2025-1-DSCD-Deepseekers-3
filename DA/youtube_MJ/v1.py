#!/usr/bin/env python
import time
import json
import os
import re
import csv
import pandas as pd
from tqdm import tqdm
from googleapiclient.discovery import build
#예뻐요, 사전 전처리
#영상부터 거르고
#외국어 거르기

API_KEY = None  # 실행창에서 입력받음

def convert_to_rfc3339(date_str, is_start=True):
    if is_start:
        return f"{date_str}T00:00:00Z"
    else:
        return f"{date_str}T23:59:59Z"

def get_video_id(url):
    from urllib.parse import urlparse, parse_qs
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['youtu.be']:
        return parsed_url.path[1:]
    elif parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        query_params = parse_qs(parsed_url.query)
        return query_params.get('v', [None])[0]
    else:
        return None

def search_videos(keyword, start_rfc, end_rfc, duration=None):
    youtube = build("youtube", "v3", developerKey=API_KEY)
    videos = []
    page_token = None
    while True:
        request = youtube.search().list(
            part="snippet",
            q=keyword,
            type="video",
            publishedAfter=start_rfc,
            publishedBefore=end_rfc,
            maxResults=50,
            pageToken=page_token,
            videoDuration=duration  # duration이 None이면 무시됨
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
    youtube = build("youtube", "v3", developerKey=API_KEY)
    details = []
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        request = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(batch_ids),
            maxResults=50
        )
        response = request.execute()
        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            statistics = item.get("statistics", {})
            details.append({
                "videoId": item["id"],
                "title": snippet.get("title", ""),
                "publishedAt": snippet.get("publishedAt", ""),
                "likeCount": statistics.get("likeCount", ""),
                "commentCount": statistics.get("commentCount", ""),
                "viewCount": statistics.get("viewCount", ""),
                "channelId": snippet.get("channelId", "")
            })
    return details

def get_comments(video_id):
    youtube = build("youtube", "v3", developerKey=API_KEY)
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
            print(f"영상 {video_id} 댓글 수집 실패: {e}")
            break

        for item in response.get("items", []):
            top_comment = item["snippet"]["topLevelComment"]
            comment_snippet = top_comment["snippet"]
            comment_id = top_comment["id"]
            published_at = comment_snippet["publishedAt"]
            comment_text = comment_snippet["textDisplay"]
            comments_info.append({
                "날짜": published_at,
                "video_id": video_id,
                "comment_id": comment_id,
                "comment_text": comment_text
            })
        page_token = response.get("nextPageToken")
        if not page_token:
            break
    return comments_info

def save_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"CSV 파일이 '{filename}'로 저장되었습니다.")

def main():
    global API_KEY
    # 사용자 입력 (인터랙티브)
    keyword = input("검색할 키워드를 입력하세요: ").strip()
    start_date = input("시작 날짜 (YYYY-MM-DD): ").strip()
    end_date = input("종료 날짜 (YYYY-MM-DD): ").strip()
    print("수집할 데이터 종류 입력 longform shorts metadata comments)")
    print("여러 개 선택 시 공백으로 구분함.")
    data_types = input("데이터 종류: ").strip().split()
    API_KEY = input("유튜브 API : ").strip()
    
    # 롱폼과 숏폼 검색 옵션을 추가로 입력받음 (기본값은 "long" 및 "short")
    longform_duration = "long"
    shorts_duration = "short"
    if "longform" in data_types:
        user_input = input("롱폼 영상 검색 옵션을 입력하세요 (기본: long): ").strip()
        if user_input:
            longform_duration = user_input
    if "shorts" in data_types:
        user_input = input("숏폼 영상 검색 옵션을 입력하세요 (기본: short): ").strip()
        if user_input:
            shorts_duration = user_input

    start_rfc = f"{start_date}T00:00:00Z"
    end_rfc = f"{end_date}T23:59:59Z"

    overall_start = time.time()

    # --- 메타데이터 및 댓글용 동영상 검색 (duration 미설정 = 전체) ---
    videos_for_meta = []
    videos_meta = []
    if "metadata" in data_types or "comments" in data_types:
        print("메타데이터 및 댓글용 동영상 검색 중...")
        videos_for_meta = search_videos(keyword, start_rfc, end_rfc, duration=None)
        print(f"검색된 동영상 개수 (메타데이터/댓글): {len(videos_for_meta)} 개")
        video_ids_meta = [v["videoId"] for v in videos_for_meta]
        if video_ids_meta:
            videos_meta = get_video_details(video_ids_meta)

    # --- 롱폼 영상 검색 ---
    videos_longform = []
    if "longform" in data_types:
        print("롱폼 영상 검색 중...")
        videos = search_videos(keyword, start_rfc, end_rfc, duration=longform_duration)
        print(f"검색된 롱폼 영상 개수: {len(videos)} 개")
        video_ids = [v["videoId"] for v in videos]
        if video_ids:
            videos_longform = get_video_details(video_ids)

    # --- 숏폼 영상 검색 ---
    videos_shorts = []
    if "shorts" in data_types:
        print("숏폼 영상 검색 중...")
        videos = search_videos(keyword, start_rfc, end_rfc, duration=shorts_duration)
        print(f"검색된 숏폼 영상 개수: {len(videos)} 개")
        video_ids = [v["videoId"] for v in videos]
        if video_ids:
            videos_shorts = get_video_details(video_ids)

    # --- CSV 저장 ---
    if "metadata" in data_types and videos_meta:
        filename = f"{keyword}_metadata_{start_date}_{end_date}.csv"
        print("메타데이터 CSV 저장 중...")
        save_csv(videos_meta, filename)

    if "longform" in data_types and videos_longform:
        filename = f"{keyword}_longform_{start_date}_{end_date}.csv"
        print("롱폼 영상 CSV 저장 중...")
        save_csv(videos_longform, filename)

    if "shorts" in data_types and videos_shorts:
        filename = f"{keyword}_shorts_{start_date}_{end_date}.csv"
        print("숏폼 영상 CSV 저장 중...")
        save_csv(videos_shorts, filename)

    if "comments" in data_types and videos_meta:
        print("댓글 수집 중...")
        comments_data = []
        for video in tqdm(videos_meta, desc="댓글 수집", unit="video"):
            vid = video["videoId"]
            comments = get_comments(vid)
            for comment in comments:
                comments_data.append(comment)
        if comments_data:
            filename = f"{keyword}_comments_{start_date}_{end_date}.csv"
            print("댓글 CSV 저장 중...")
            save_csv(comments_data, filename)

    overall_end = time.time()
    elapsed = overall_end - overall_start
    print(f"\n데이터 수집 완료. 걸린 시간: {elapsed:.2f} 초.")

if __name__ == "__main__":
    main()
