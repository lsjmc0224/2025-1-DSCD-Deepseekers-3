"""
YouTube API 키 직접 테스트 스크립트

이 스크립트는 Google YouTube Data API를 직접 호출하여 API 키가 유효한지 확인합니다.
"""

import os
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

def test_youtube_api():
    """YouTube API 키 테스트"""
    # .env 파일에서 환경 변수 로드
    load_dotenv("backend/.env")
    
    # YouTube API 키 가져오기
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    if not youtube_api_key:
        print("오류: YOUTUBE_API_KEY 환경 변수를 찾을 수 없습니다.")
        return False
    
    print(f"API 키: {youtube_api_key[:5]}...{youtube_api_key[-5:]}")
    
    try:
        # YouTube API 클라이언트 초기화
        youtube = build("youtube", "v3", developerKey=youtube_api_key)
        
        # 간단한 API 호출로 유효성 검증
        request = youtube.videos().list(
            part="snippet,statistics",
            id="a6zqFsriDlQ"  # 테스트용 비디오 ID
        )
        response = request.execute()
        
        # 응답 확인
        if "items" in response and len(response["items"]) > 0:
            video = response["items"][0]
            print("\n✅ YouTube API 키가 유효합니다!")
            print("\n비디오 정보:")
            print(f"제목: {video['snippet']['title']}")
            print(f"채널: {video['snippet']['channelTitle']}")
            print(f"조회수: {video['statistics']['viewCount']}")
            print(f"좋아요: {video['statistics'].get('likeCount', 'N/A')}")
            print(f"댓글 수: {video['statistics'].get('commentCount', 'N/A')}")
            return True
        else:
            print("\n❌ API는 응답했지만 비디오 정보를 찾을 수 없습니다.")
            print(f"응답: {json.dumps(response, indent=2)}")
            return False
            
    except HttpError as e:
        error_content = json.loads(e.content.decode("utf-8"))
        print(f"\n❌ YouTube API 오류 발생: {error_content['error']['message']}")
        print(f"오류 코드: {error_content['error']['code']}")
        print(f"오류 상태: {error_content['error']['status']}")
        return False
        
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    print("===== YouTube API 키 직접 테스트 =====\n")
    test_youtube_api()
    print("\n===== 테스트 완료 =====") 