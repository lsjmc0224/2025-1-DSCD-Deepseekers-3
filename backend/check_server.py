"""
백엔드 서버 연결 및 API 엔드포인트 확인 스크립트
"""

import requests
import sys

def check_server_connection(base_url="http://localhost:8000"):
    """서버 연결 상태 확인"""
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        print(f"서버 연결 상태: {'성공' if response.status_code == 200 else '실패'}")
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"서버 연결 중 오류 발생: {str(e)}")
        return False

def check_api_docs(base_url="http://localhost:8000"):
    """API 문서 접근 가능 여부 확인"""
    try:
        response = requests.get(f"{base_url}/api/v1/openapi.json")
        print(f"API 문서 상태: {'성공' if response.status_code == 200 else '실패'}")
        print(f"상태 코드: {response.status_code}")
        if response.status_code == 200:
            api_spec = response.json()
            paths = list(api_spec.get("paths", {}).keys())
            print(f"사용 가능한 API 엔드포인트: {len(paths)}")
            for path in paths:
                print(f"  - {path}")
        return response.status_code == 200
    except Exception as e:
        print(f"API 문서 접근 중 오류 발생: {str(e)}")
        return False

def test_youtube_endpoint(base_url="http://localhost:8000"):
    """YouTube 데이터 수집 엔드포인트 테스트"""
    try:
        url = f"{base_url}/api/v1/data-collection/youtube"
        payload = {
            "video_ids": ["a6zqFsriDlQ"],
            "max_comments": 10
        }
        print(f"엔드포인트 요청: {url}")
        print(f"요청 데이터: {payload}")
        response = requests.post(url, json=payload)
        print(f"상태 코드: {response.status_code}")
        print(f"응답 헤더: {dict(response.headers)}")
        print(f"응답 본문: {response.text}")
        return response.status_code == 202
    except Exception as e:
        print(f"YouTube 엔드포인트 테스트 중 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    base_url = "http://localhost:8000"
    print(f"서버 URL: {base_url}")
    
    # 서버 연결 확인
    print("\n1. 서버 연결 확인")
    if not check_server_connection(base_url):
        print("서버 연결에 실패했습니다. 서버가 실행 중인지 확인하세요.")
        sys.exit(1)
    
    # API 문서 확인
    print("\n2. API 문서 확인")
    check_api_docs(base_url)
    
    # YouTube 엔드포인트 테스트
    print("\n3. YouTube 데이터 수집 엔드포인트 테스트")
    test_youtube_endpoint(base_url)
    
    print("\n검사 완료!") 