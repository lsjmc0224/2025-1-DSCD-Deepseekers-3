#!/usr/bin/env python
"""
YouTube 데이터 수집 명령행 유틸리티

사용법:
    python collect_youtube_data.py --video_id VIDEO_ID [--max_comments MAX_COMMENTS] [--output OUTPUT]
    python collect_youtube_data.py --keyword KEYWORD [--max_videos MAX_VIDEOS] [--max_comments MAX_COMMENTS] [--output OUTPUT]

예시:
    python collect_youtube_data.py --video_id dQw4w9WgXcQ --max_comments 50 --output data/youtube_data.json
    python collect_youtube_data.py --keyword "편의점 디저트" --max_videos 5 --max_comments 30 --output data/dessert_videos.json
"""

import os
import sys
import json
import argparse
import asyncio
from datetime import datetime


# 상위 디렉토리를 경로에 추가하여 app 모듈 가져오기
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.services.collectors.youtube import collect_youtube_data


class DateTimeEncoder(json.JSONEncoder):
    """
    날짜/시간 객체를 JSON으로 직렬화하기 위한 인코더
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


async def main():
    parser = argparse.ArgumentParser(description='YouTube 데이터 수집 유틸리티')
    
    # 비디오 ID 또는 키워드 인자 (둘 중 하나는 필수)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--video_id', type=str, help='데이터를 수집할 YouTube 비디오 ID')
    group.add_argument('--keyword', type=str, help='검색할 키워드')
    
    # 선택적 인자
    parser.add_argument('--max_videos', type=int, default=10, help='키워드 검색 시 수집할 최대 비디오 수 (기본값: 10)')
    parser.add_argument('--max_comments', type=int, default=100, help='각 비디오당 수집할 최대 댓글 수 (기본값: 100)')
    parser.add_argument('--output', type=str, default='youtube_data.json', help='출력 파일 경로 (기본값: youtube_data.json)')
    
    args = parser.parse_args()
    
    # API 키 확인
    if not settings.YOUTUBE_API_KEY:
        print("오류: YOUTUBE_API_KEY가 설정되지 않았습니다.")
        print("환경 변수를 설정하거나 .env 파일에 추가하세요.")
        sys.exit(1)
    
    try:
        # 인자에 따라 수집 함수 호출
        if args.video_id:
            print(f"비디오 ID {args.video_id}에서 댓글 수집 중...")
            result = await collect_youtube_data(
                video_ids=[args.video_id], 
                max_comments=args.max_comments
            )
        else:
            print(f"키워드 '{args.keyword}'로 비디오 검색 및 댓글 수집 중...")
            result = await collect_youtube_data(
                keywords=[args.keyword], 
                max_comments=args.max_comments
            )
        
        # 결과 출력
        print(f"수집 완료: {result['video_count']}개 비디오, {result['comment_count']}개 댓글")
        
        # 결과를 JSON 파일로 저장
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
            
        print(f"결과가 {args.output}에 저장되었습니다.")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 