#!/usr/bin/env python
"""
YouTube 비디오 분석 스크립트.

사용법:
  python analyze_youtube_video.py [options] <video_id_or_url>

옵션:
  --save              분석 결과를 저장합니다.
  --no-comments       댓글을 수집하지 않습니다.
  --no-transcript     자막을 수집하지 않습니다.
  --no-channel        채널 정보를 수집하지 않습니다.
  --max-comments=N    수집할 최대 댓글 수를 지정합니다 (기본값: 100).
  --output-dir=DIR    결과를 저장할 디렉토리를 지정합니다 (기본값: data).
  --visualize         시각화를 위한 JSON 파일을 생성합니다.
  --api-key=KEY       YouTube API 키를 지정합니다.
  
예시:
  python analyze_youtube_video.py dQw4w9WgXcQ
  python analyze_youtube_video.py --save --max-comments=200 https://www.youtube.com/watch?v=dQw4w9WgXcQ
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional

# 상위 디렉토리를 sys.path에 추가하여 app 패키지를 import할 수 있도록 함
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app.services.analyzers.youtube_analyzer import YouTubeAnalyzer
except ImportError:
    print("YouTubeAnalyzer 모듈을 import할 수 없습니다.")
    print("스크립트를 backend 디렉토리에서 실행하세요.")
    sys.exit(1)

def parse_arguments() -> argparse.Namespace:
    """명령줄 인수를 파싱합니다."""
    parser = argparse.ArgumentParser(description="YouTube 비디오 분석 스크립트")
    
    parser.add_argument("video_id_or_url", help="YouTube 비디오 ID 또는 URL")
    parser.add_argument("--save", action="store_true", help="분석 결과를 저장합니다.")
    parser.add_argument("--no-comments", action="store_true", help="댓글을 수집하지 않습니다.")
    parser.add_argument("--no-transcript", action="store_true", help="자막을 수집하지 않습니다.")
    parser.add_argument("--no-channel", action="store_true", help="채널 정보를 수집하지 않습니다.")
    parser.add_argument("--max-comments", type=int, default=100, help="수집할 최대 댓글 수 (기본값: 100)")
    parser.add_argument("--output-dir", default="data", help="결과를 저장할 디렉토리 (기본값: data)")
    parser.add_argument("--visualize", action="store_true", help="시각화를 위한 JSON 파일을 생성합니다.")
    parser.add_argument("--api-key", help="YouTube API 키")
    
    return parser.parse_args()

def print_metadata(metadata: Dict[str, Any]):
    """비디오 메타데이터를 출력합니다."""
    print("\n=== 비디오 메타데이터 ===")
    print(f"ID: {metadata.get('video_id')}")
    print(f"제목: {metadata.get('title')}")
    print(f"채널: {metadata.get('channel_title')}")
    print(f"게시일: {metadata.get('published_at')}")
    print(f"조회수: {metadata.get('view_count')}")
    print(f"좋아요 수: {metadata.get('like_count')}")
    print(f"댓글 수: {metadata.get('comment_count')}")
    
    duration = metadata.get('duration_seconds', 0)
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    
    duration_str = ""
    if hours:
        duration_str += f"{hours}시간 "
    if minutes:
        duration_str += f"{minutes}분 "
    duration_str += f"{seconds}초"
    
    print(f"영상 길이: {duration_str}")

def print_channel_info(channel_info: Dict[str, Any]):
    """채널 정보를 출력합니다."""
    if not channel_info:
        return
        
    print("\n=== 채널 정보 ===")
    print(f"채널명: {channel_info.get('title')}")
    print(f"구독자 수: {channel_info.get('subscriber_count')}")
    print(f"영상 수: {channel_info.get('video_count')}")
    print(f"총 조회수: {channel_info.get('view_count')}")

def print_sentiment_analysis(sentiment_analysis: Dict[str, Any]):
    """감성 분석 결과를 출력합니다."""
    if not sentiment_analysis:
        return
        
    print("\n=== 감성 분석 결과 ===")
    
    distribution = sentiment_analysis.get("distribution", {})
    positive = distribution.get("positive", 0) * 100
    neutral = distribution.get("neutral", 0) * 100
    negative = distribution.get("negative", 0) * 100
    
    print(f"긍정적 댓글: {positive:.1f}%")
    print(f"중립적 댓글: {neutral:.1f}%")
    print(f"부정적 댓글: {negative:.1f}%")
    print(f"평균 감성 점수: {sentiment_analysis.get('average_score', 0):.2f}")
    print(f"분석된 댓글 수: {sentiment_analysis.get('comment_count', 0)}")

def print_keyword_analysis(keyword_analysis: Dict[str, Any]):
    """키워드 분석 결과를 출력합니다."""
    if not keyword_analysis:
        return
        
    print("\n=== 키워드 분석 결과 ===")
    
    # 상위 10개 키워드
    keywords = keyword_analysis.get("keywords", [])[:10]
    if keywords:
        print("주요 키워드:")
        for i, (keyword, score) in enumerate(keywords, 1):
            print(f"  {i}. {keyword} ({score:.4f})")
    
    # 카테고리별 키워드
    categorized = keyword_analysis.get("categorized_keywords", {})
    if categorized:
        print("\n카테고리별 키워드:")
        for category, cat_keywords in categorized.items():
            print(f"  {category}:")
            for keyword, score in cat_keywords[:3]:  # 각 카테고리별 상위 3개
                print(f"    - {keyword} ({score:.4f})")

def print_transcript_analysis(transcript_analysis: Dict[str, Any]):
    """자막 분석 결과를 출력합니다."""
    if not transcript_analysis:
        return
        
    print("\n=== 자막 분석 결과 ===")
    print(f"자막 문장 수: {transcript_analysis.get('sentence_count', 0)}")
    print(f"자막 텍스트 길이: {transcript_analysis.get('transcript_length', 0)} 자")
    
    # 상위 5개 키워드
    keywords = transcript_analysis.get("keywords", [])[:5]
    if keywords:
        print("주요 키워드:")
        for i, (keyword, score) in enumerate(keywords, 1):
            print(f"  {i}. {keyword} ({score:.4f})")

def main():
    """메인 함수"""
    # 인수 파싱
    args = parse_arguments()
    
    # API 키 설정
    api_key = args.api_key or os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("YouTube API 키가 설정되지 않았습니다.")
        print("API 키를 --api-key 옵션으로 제공하거나 YOUTUBE_API_KEY 환경 변수를 설정하세요.")
        sys.exit(1)
    
    # YouTube 분석기 초기화
    analyzer = YouTubeAnalyzer(api_key=api_key)
    
    # 시작 메시지
    print(f"YouTube 비디오 분석: {args.video_id_or_url}")
    print("분석 중...")
    
    try:
        # 비디오 데이터 수집 및 분석
        analysis_result = analyzer.analyze(
            video_id_or_url=args.video_id_or_url,
            save_results=args.save,
            output_dir=args.output_dir
        )
        
        # 에러 처리
        if "error" in analysis_result:
            print(f"오류: {analysis_result['error']}")
            sys.exit(1)
        
        # 결과 출력
        print_metadata(analysis_result.get("metadata", {}))
        print_channel_info(analysis_result.get("channel_info", {}))
        print_sentiment_analysis(analysis_result.get("sentiment_analysis", {}))
        print_keyword_analysis(analysis_result.get("keyword_analysis", {}))
        print_transcript_analysis(analysis_result.get("transcript_analysis", {}))
        
        # 시각화용 파일 생성
        if args.visualize:
            viz_file = analyzer.save_for_visualization(
                analysis_result,
                output_dir=os.path.join(args.output_dir, "visualization")
            )
            print(f"\n시각화용 JSON 파일이 생성되었습니다: {viz_file}")
        
        # 완료 메시지
        print("\n분석이 완료되었습니다!")
        
    except Exception as e:
        print(f"분석 중 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 