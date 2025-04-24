#!/usr/bin/env python
"""
YouTube 비디오를 검색하고 분석하는 스크립트
"""
import os
import sys
import argparse
import re
from pathlib import Path
import subprocess

def extract_video_id(url):
    """YouTube URL에서 비디오 ID를 추출합니다."""
    # 정규 표현식 패턴
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:shorts\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # URL이 아닌 경우 직접 비디오 ID로 간주
    if re.match(r'^[0-9A-Za-z_-]{11}$', url):
        return url
    
    return None

def run_analysis(video_id):
    """비디오 ID를 사용하여 분석 프로세스를 실행합니다."""
    print(f"[*] 비디오 ID: {video_id} 분석 시작")
    
    # 데이터 수집 스크립트 실행
    try:
        print("[*] 비디오 데이터 수집 중...")
        subprocess.run(
            [sys.executable, "simple_test.py", "--video_id", video_id],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[!] 데이터 수집 오류: {e}")
        return False
    
    # 분석 스크립트 실행
    try:
        print("[*] 수집된 데이터 분석 중...")
        subprocess.run(
            [sys.executable, "analyze_test.py"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[!] 데이터 분석 오류: {e}")
        return False
    
    # 시각화 스크립트 실행
    try:
        print("[*] 분석 결과 시각화 중...")
        subprocess.run(
            [sys.executable, "visualize_data.py"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[!] 데이터 시각화 오류: {e}")
    
    print(f"[*] 비디오 ID: {video_id} 분석 완료")
    print(f"[*] API 서버에서 결과를 확인하세요: http://localhost:8000/docs")
    return True

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="YouTube 비디오 검색 및 분석")
    parser.add_argument(
        "url", 
        help="YouTube 비디오 URL 또는 비디오 ID"
    )
    
    args = parser.parse_args()
    
    # 비디오 ID 추출
    video_id = extract_video_id(args.url)
    
    if not video_id:
        print("[!] 유효한 YouTube URL 또는 비디오 ID가 아닙니다.")
        sys.exit(1)
    
    # 분석 실행
    if run_analysis(video_id):
        print("[*] 분석이 성공적으로 완료되었습니다.")
    else:
        print("[!] 분석 중 오류가 발생했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main() 