"""
통합된 YouTube 수집기 테스트 스크립트

이 스크립트는 youtube_collector.py의 주요 기능을 테스트합니다.
"""
import os
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 경로를 추가하여 모듈 임포트 가능하게 함
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.collectors.youtube_collector import (
    collect_youtube_data,
    extract_video_id,
    get_video_metadata,
    get_video_comments,
    get_video_transcript
)

async def test_video_metadata():
    """비디오 메타데이터 가져오기 테스트"""
    print("=== 비디오 메타데이터 테스트 ===")
    # 테스트할 비디오 ID (편의점 디저트 관련 비디오)
    video_id = "wgyVwOE-V5U"  # 예시 ID
    
    metadata = await get_video_metadata(video_id)
    if metadata:
        print(f"제목: {metadata.get('title')}")
        print(f"조회수: {metadata.get('view_count')}")
        print(f"좋아요: {metadata.get('like_count')}")
        print(f"채널: {metadata.get('channel_title')}")
    else:
        print("메타데이터를 가져오지 못했습니다.")

async def test_video_comments():
    """비디오 댓글 가져오기 테스트"""
    print("\n=== 비디오 댓글 테스트 ===")
    video_id = "wgyVwOE-V5U"  # 예시 ID
    
    comments = await get_video_comments(video_id, max_comments=5, sort_by='time')
    print(f"{len(comments)}개 댓글 수집됨:")
    
    for i, comment in enumerate(comments[:5], 1):
        print(f"{i}. {comment.get('author')}: {comment.get('text')[:50]}...")

async def test_video_transcript():
    """비디오 자막 가져오기 테스트"""
    print("\n=== 비디오 자막 테스트 ===")
    video_id = "wgyVwOE-V5U"  # 예시 ID
    
    transcript = await get_video_transcript(video_id)
    if transcript:
        print(f"{len(transcript)}개 자막 항목 수집됨")
        print(f"자막 예시: {transcript[0] if transcript else ''}")
    else:
        print("자막을 가져오지 못했습니다.")

async def test_full_collection():
    """전체 데이터 수집 테스트"""
    print("\n=== 전체 데이터 수집 테스트 ===")
    
    # URL 예시
    video_url = "https://youtu.be/wgyVwOE-V5U"
    video_id = extract_video_id(video_url)
    
    print(f"URL에서 추출한 비디오 ID: {video_id}")
    
    if video_id:
        result = await collect_youtube_data(
            video_id,
            max_comments=10,
            comment_sort='time',
            save_to_file=True
        )
        
        if result:
            print(f"영상 제목: {result.get('title')}")
            print(f"수집된 댓글 수: {len(result.get('comments', []))}")
            print(f"자막 항목 수: {len(result.get('transcript', []))}")
            
            # 직접 JSON 파일로 저장
            data_dir = Path("data/youtube")
            data_dir.mkdir(parents=True, exist_ok=True)
            filename = f"video_{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = data_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
                
            print(f"데이터 저장 완료: {file_path}")
        else:
            print("데이터 수집 실패")

async def main():
    """메인 테스트 함수"""
    print("YouTube 수집기 테스트 시작")
    
    # 각 기능 테스트
    await test_video_metadata()
    await test_video_comments()
    await test_video_transcript()
    await test_full_collection()
    
    print("\n모든 테스트 완료")

if __name__ == "__main__":
    # 데이터 디렉토리 생성
    os.makedirs("data/youtube", exist_ok=True)
    
    # 비동기 테스트 실행
    asyncio.run(main()) 