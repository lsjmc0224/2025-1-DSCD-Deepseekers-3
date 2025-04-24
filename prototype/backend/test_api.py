"""
YouTube API 통합 테스트 스크립트

이 스크립트는 YouTube API 키와 백엔드 API 서버의 통합을 테스트합니다.
* YouTube 데이터 수집 API 엔드포인트 테스트
* YouTube API 키 유효성 검증
* 비동기 작업 상태 추적 테스트
"""

import requests
import time
import json

# API 엔드포인트 설정
BASE_URL = "http://localhost:8000/api/v1"
COLLECTION_ENDPOINT = f"{BASE_URL}/data-collection/youtube"
STATUS_ENDPOINT = f"{BASE_URL}/data-collection/status"

def test_youtube_data_collection():
    """YouTube 데이터 수집 API 엔드포인트 테스트"""
    
    # 1. 테스트 비디오 ID (인기 있는 편의점 디저트 리뷰 영상)
    video_id = "a6zqFsriDlQ"
    
    # 2. 데이터 수집 요청
    print(f"YouTube 비디오 ID {video_id}에 대한 데이터 수집 요청 중...")
    
    payload = {
        "video_ids": [video_id],
        "max_comments": 10  # 테스트를 위해 댓글 수 제한
    }
    
    response = requests.post(COLLECTION_ENDPOINT, json=payload)
    
    if response.status_code != 202:  # 202 Accepted
        print(f"오류: 예상되는 상태 코드는 202지만, {response.status_code}를 받았습니다.")
        print(f"응답: {response.text}")
        return False
    
    print(f"응답: {response.json()}")
    
    # 3. 요청 ID 추출
    request_id = response.json().get("request_id")
    
    if not request_id:
        print("오류: 응답에서 request_id를 찾을 수 없습니다.")
        return False
    
    print(f"요청 ID: {request_id}")
    
    # 4. 작업 상태 추적
    print("\n작업 상태 추적 중...")
    
    max_retries = 10
    retry_count = 0
    completed = False
    
    while retry_count < max_retries and not completed:
        status_response = requests.get(f"{STATUS_ENDPOINT}/{request_id}")
        
        if status_response.status_code != 200:
            print(f"오류: 상태 조회 실패. 상태 코드: {status_response.status_code}")
            print(f"응답: {status_response.text}")
            return False
        
        status_data = status_response.json()
        status = status_data.get("status")
        progress = status_data.get("progress", 0)
        message = status_data.get("message", "")
        
        print(f"상태: {status}, 진행률: {progress}%, 메시지: {message}")
        
        if status in ["completed", "error"]:
            completed = True
            if status == "completed":
                print("\n데이터 수집 완료!")
                if status_data.get("result"):
                    print(f"결과 요약: {len(status_data['result'].get('videos', []))} 개의 비디오, "
                          f"{len(status_data['result'].get('comments', []))} 개의 댓글 수집됨")
            else:
                print(f"\n데이터 수집 중 오류 발생: {message}")
        
        retry_count += 1
        if not completed and retry_count < max_retries:
            print("5초 후 상태 다시 확인...")
            time.sleep(5)
    
    if not completed:
        print(f"\n최대 재시도 횟수({max_retries})에 도달했지만 작업이 완료되지 않았습니다.")
        return False
    
    return True

if __name__ == "__main__":
    print("===== YouTube API 통합 테스트 시작 =====\n")
    success = test_youtube_data_collection()
    
    if success:
        print("\n✅ 테스트 성공: YouTube API 통합이 정상적으로 작동합니다.")
    else:
        print("\n❌ 테스트 실패: YouTube API 통합에 문제가 있습니다.")
        print("- .env 파일의 YOUTUBE_API_KEY가 올바르게 설정되었는지 확인하세요.")
        print("- 백엔드 서버가 실행 중인지 확인하세요.")
        print("- 로그에서 추가 오류 정보를 확인하세요.")
    
    print("\n===== YouTube API 통합 테스트 종료 =====") 