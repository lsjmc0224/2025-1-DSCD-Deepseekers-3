import re
import csv
import os
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from googleapiclient.discovery import build

# YouTube API 키
API_KEY = "AIzaSyD4vHPeA4MUNJtjOtXgEwPiX4QFHssxmSQ"

def get_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['youtu.be']:
        return parsed_url.path[1:]  # 앞의 '/' 제거
    elif parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        query_params = parse_qs(parsed_url.query)
        return query_params.get('v', [None])[0]
    else:
        return None

def get_video_metadata(video_id, api_key):
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )
    response = request.execute()
    if response.get("items"):
        item = response["items"][0]
        snippet = item["snippet"]
        statistics = item["statistics"]
        metadata = {
            "title": snippet.get("title", "Untitled"),
            "likeCount": statistics.get("likeCount", "N/A"),
            "commentCount": statistics.get("commentCount", "N/A"),
            "viewCount": statistics.get("viewCount", "N/A"),
            "publishedAt": snippet.get("publishedAt", "N/A"),
            "channelId": snippet.get("channelId")
        }
        return metadata
    else:
        return None

def get_channel_subscriber_count(channel_id, api_key):
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.channels().list(
        part="statistics",
        id=channel_id
    )
    response = request.execute()
    if response.get("items"):
        stats = response["items"][0]["statistics"]
        return stats.get("subscriberCount", "N/A")
    else:
        return "N/A"

def sanitize_filename(filename):
    # 파일명에 사용할 수 없는 문자 제거
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def split_into_sentences(text):
    """
    마침표, 물음표, 느낌표, 줄임표(…) 뒤를 기준으로 문장 분할.
    여러 문장부호(...)가 연속되면 하나의 종결부호로 취급.
    """
    # 정규식 설명:
    #   ([^.?!…]+)   => 종결부호가 나오기 전까지의 글자들
    #   [\.?!…]+     => 마침표/물음표/느낌표/줄임표가 한 번 이상
    pattern = r'([^.?!…]+[.?!…]+)'
    matches = re.findall(pattern, text)

    sentences = []
    for m in matches:
        s = m.strip()
        if s:
            sentences.append(s)

    # 혹시 마지막 문장 끝에 종결부호가 없어 남은 글자가 있다면 추가
    remainder = re.sub(pattern, '', text).strip()
    if remainder:
        sentences.append(remainder)

    return sentences

def main():
    # 분석할 동영상 URL
    video_url = "https://youtu.be/wgyVwOE-V5U?si=PZCR5zLcaM_t91y9"
    video_id = get_video_id(video_url)

    # 자막(한국어 캡션) 추출
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
    text_formatter = TextFormatter()  # SRT 형식으로 출력
    text_formatted = text_formatter.format_transcript(transcript)
    # 개행문자 제거하여 하나의 긴 문자열로 변환
    transcript_text = text_formatted.replace("\n", " ")

    # 영상 메타데이터 추출
    metadata = get_video_metadata(video_id, API_KEY)
    if metadata is None:
        print("메타데이터를 가져올 수 없습니다.")
        return

    # 채널 구독자 수 추출
    subscriber_count = get_channel_subscriber_count(metadata["channelId"], API_KEY)

    # 자막을 문장 단위로 분할 (업그레이드된 정규식)
    sentences = split_into_sentences(transcript_text)

    # CSV 파일명 (영상 제목 기반)
    file_name = sanitize_filename(metadata["title"]) + ".csv"

    with open(file_name, mode="w", encoding="utf-8-sig", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # 첫 번째 행(두 줄): 메타데이터
        writer.writerow(["Like Count", "Subscriber Count", "Comment Count", "View Count", "Upload Date"])
        writer.writerow([
            metadata["likeCount"],
            subscriber_count,
            metadata["commentCount"],
            metadata["viewCount"],
            metadata["publishedAt"]
        ])

        # 세 번째 행부터: 문장 하나당 한 행
        for sentence in sentences:
            # 필요하다면 문장 끝의 종결부호 유지 / 제거 등 선택 가능
            writer.writerow([sentence])

    print(f"CSV 파일 '{file_name}'이(가) 생성되었습니다.")

if __name__ == '__main__':
    main()
