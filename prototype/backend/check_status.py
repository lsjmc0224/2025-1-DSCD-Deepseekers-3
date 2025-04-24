"""
데이터 수집 작업 상태 확인 스크립트
"""

import requests
import json
import sys
import time

def check_collection_status(request_id, base_url="http://localhost:8000", max_retries=10, retry_delay=5):
    """데이터 수집 작업 상태 확인"""
    url = f"{base_url}/api/v1/data-collection/status/{request_id}"
    
    print(f"작업 상태 확인 중: {request_id}")
    print(f"URL: {url}")
    
    for attempt in range(max_retries):
        try:
            print(f"\n시도 {attempt + 1}/{max_retries}:")
            response = requests.get(url)
            print(f"상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"상태: {data.get('status')}")
                print(f"진행률: {data.get('progress')}%")
                print(f"메시지: {data.get('message')}")
                
                # 완료 또는 오류 상태인 경우 결과 출력
                if data.get('status') in ["completed", "error"]:
                    print("\n작업 완료 또는 오류:")
                    if data.get('result'):
                        print("결과:")
                        result = data.get('result')
                        print(json.dumps(result, indent=2, ensure_ascii=False))
                    return True
            else:
                print(f"오류 응답: {response.text}")
            
            if attempt < max_retries - 1:
                print(f"{retry_delay}초 후 다시 시도...")
                time.sleep(retry_delay)
            
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            if attempt < max_retries - 1:
                print(f"{retry_delay}초 후 다시 시도...")
                time.sleep(retry_delay)
    
    print(f"\n최대 시도 횟수({max_retries})에 도달했습니다.")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python check_status.py <request_id>")
        print("예: python check_status.py youtube-54fa21e0-b007-403c-b7f0-46350feacad2")
        sys.exit(1)
    
    request_id = sys.argv[1]
    check_collection_status(request_id) 