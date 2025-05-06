#!/usr/bin/env python
"""
YouTube ETL 파이프라인 실행 스크립트

이 스크립트는 명령줄에서 YouTube ETL 파이프라인을 직접 실행할 수 있게 합니다.
Prefect 워크플로우 배포 없이 파이프라인을 즉시 실행하고 싶을 때 사용합니다.
"""
import sys
import os
import argparse
import asyncio
from pathlib import Path

# 상위 디렉토리를 경로에 추가하여 모듈 임포트 가능하게 함
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipelines.youtube import youtube_etl_pipeline


def parse_arguments():
    """
    명령줄 인수를 파싱합니다.
    """
    parser = argparse.ArgumentParser(description="YouTube ETL 파이프라인 실행")
    
    parser.add_argument(
        "--max-videos", 
        type=int, 
        default=3,
        help="각 키워드당 수집할 최대 동영상 수 (기본값: 3)"
    )
    
    parser.add_argument(
        "--max-comments", 
        type=int, 
        default=100,
        help="각 동영상당 수집할 최대 댓글 수 (기본값: 100)"
    )
    
    parser.add_argument(
        "--keywords-only",
        action="store_true",
        help="키워드 검색으로만 동영상 수집 (크리에이터 채널 동영상 수집 제외)"
    )
    
    parser.add_argument(
        "--creators-only",
        action="store_true",
        help="크리에이터 채널에서만 동영상 수집 (키워드 검색 제외)"
    )
    
    parser.add_argument(
        "--skip-preprocessing",
        action="store_true",
        help="댓글 전처리 단계 건너뛰기"
    )
    
    parser.add_argument(
        "--skip-keyword-extraction",
        action="store_true",
        help="키워드 추출 단계 건너뛰기"
    )
    
    parser.add_argument(
        "--skip-database",
        action="store_true",
        help="데이터베이스 저장 단계 건너뛰기"
    )
    
    return parser.parse_args()


def main():
    """
    YouTube ETL 파이프라인을 실행합니다.
    """
    args = parse_arguments()
    
    # 파이프라인 매개변수 설정
    params = {
        "max_videos_per_keyword": args.max_videos,
        "max_comments_per_video": args.max_comments,
        "collect_from_keywords": not args.creators_only,
        "collect_from_creators": not args.keywords_only,
        "run_preprocessing": not args.skip_preprocessing,
        "run_keyword_extraction": not args.skip_keyword_extraction,
        "save_to_database": not args.skip_database,
    }
    
    print("YouTube ETL 파이프라인 실행 시작")
    print(f"파라미터: {params}")
    
    # 파이프라인 실행
    result = youtube_etl_pipeline(**params)
    
    print("\n파이프라인 실행 결과:")
    print(f"수집된 동영상: {result.get('total_videos', 0)}")
    print(f"수집된 댓글: {result.get('total_comments', 0)}")
    print(f"추출된 키워드: {result.get('total_keywords', 0)}")
    print("YouTube ETL 파이프라인 실행 완료")


if __name__ == "__main__":
    main() 