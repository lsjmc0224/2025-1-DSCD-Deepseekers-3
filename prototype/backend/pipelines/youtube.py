#!/usr/bin/env python
"""
YouTube ETL 파이프라인 모듈

이 모듈은 Prefect를 사용하여 YouTube API에서 동영상, 댓글을 수집하고
분석하는 ETL 파이프라인을 구현합니다.
"""

import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set

from prefect import flow, task, get_run_logger
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import IntervalSchedule

# 서비스 모듈 임포트
from app.services.collectors import (
    collect_youtube_data,
    generate_request_id,
    get_collection_status
)
from app.services.analysis.sentiment_analyzer import SentimentAnalyzer
from app.services.analysis.keyword_extractor import KeywordExtractor

# 데이터 디렉토리 설정
DATA_DIR = Path("data/youtube")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 편의점 디저트 관련 키워드 목록
PRODUCT_KEYWORDS = [
    "편의점 디저트", "편의점 케이크", "편의점 빵", "편의점 스위트", "편의점 과자",
    "편의점 신상 디저트", "편의점 푸딩", "편의점 쿠키", "편의점 초콜릿", "편의점 아이스크림"
]


@task(name="check-video-ids-task", retries=3, retry_delay_seconds=5)
async def check_video_ids(video_ids: List[str]) -> List[str]:
    """
    비디오 ID 목록의 유효성을 확인하는 태스크
    
    Args:
        video_ids: 확인할 비디오 ID 목록
        
    Returns:
        유효한 비디오 ID 목록
    """
    logger = get_run_logger()
    logger.info(f"비디오 ID 유효성 검사 시작 - {len(video_ids)}개 ID")
    
    valid_ids = []
    
    for video_id in video_ids:
        # 유효한 YouTube 비디오 ID 형식 확인 (일반적으로 11자리)
        if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
            valid_ids.append(video_id)
        else:
            logger.warning(f"유효하지 않은 비디오 ID 형식: {video_id}")
    
    logger.info(f"유효한 비디오 ID: {len(valid_ids)}개")
    return valid_ids


@task(name="collect-youtube-videos-task", retries=2)
async def collect_videos_task(
    video_ids: List[str],
    max_comments: int = 100
) -> Dict[str, Any]:
    """
    YouTube 동영상 및 댓글을 수집하는 태스크
    
    Args:
        video_ids: 수집할 비디오 ID 목록
        max_comments: 비디오당 최대 수집 댓글 수
        
    Returns:
        수집 결과 데이터
    """
    logger = get_run_logger()
    logger.info(f"YouTube 데이터 수집 시작 - {len(video_ids)}개 비디오, "
                f"비디오당 최대 댓글: {max_comments}")
    
    collected_data = {}
    
    # 수집 요청 ID 생성
    request_id = generate_request_id()
    
    try:
        # 비동기 데이터 수집 작업 시작
        result = await collect_youtube_data(
            video_ids=video_ids,
            max_comments=max_comments
        )
        
        logger.info(f"데이터 수집 작업 시작됨 - 요청 ID: {result.get('request_id')}")
        
        # 수집 상태 확인
        status = await get_collection_status(request_id)
        logger.info(f"수집 상태: {status.get('status')}, 진행률: {status.get('progress')}%")
        
        # 수집 완료 대기 (실제 구현에서는 비동기 폴링 로직 필요)
        # 이 예제에서는 간단히 처리
        if status.get('status') == 'completed':
            collected_data = status.get('result', {})
            logger.info(f"데이터 수집 완료 - {len(collected_data.get('videos', []))}개 비디오, "
                      f"{collected_data.get('total_comments', 0)}개 댓글")
        else:
            logger.warning(f"데이터 수집이 완료되지 않음 - 상태: {status.get('status')}")
        
    except Exception as e:
        logger.error(f"데이터 수집 중 오류 발생: {str(e)}")
    
    return collected_data


@task(name="analyze-sentiment-task")
async def analyze_sentiment_task(collection_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    수집된 댓글에 대한 감성 분석을 수행하는 태스크
    
    Args:
        collection_results: 수집 결과 데이터
        
    Returns:
        감성 분석 결과
    """
    logger = get_run_logger()
    logger.info("감성 분석 시작")
    
    videos = collection_results.get("videos", [])
    if not videos:
        logger.warning("분석할 비디오 데이터가 없습니다.")
        return {"sentiment_results": []}
    
    # 감성 분석기 초기화
    analyzer = SentimentAnalyzer()
    
    sentiment_results = []
    total_comments = 0
    
    for video in videos:
        video_id = video.get("video_id")
        comments = video.get("comments", [])
        
        if not comments:
            logger.warning(f"비디오 '{video_id}'에 분석할 댓글이 없습니다.")
            continue
        
        logger.info(f"비디오 '{video_id}'의 {len(comments)}개 댓글 감성 분석 중...")
        
        try:
            # 댓글 감성 분석
            analyzed_comments = []
            
            for comment in comments:
                text = comment.get("text_original", "")
                if not text:
                    continue
                
                sentiment = analyzer.analyze(text)
                analyzed_comment = {
                    **comment,
                    "sentiment": sentiment
                }
                analyzed_comments.append(analyzed_comment)
                total_comments += 1
            
            # 비디오별 감성 분석 결과 취합
            positive_count = sum(1 for c in analyzed_comments if c["sentiment"]["sentiment"] == "positive")
            negative_count = sum(1 for c in analyzed_comments if c["sentiment"]["sentiment"] == "negative")
            neutral_count = sum(1 for c in analyzed_comments if c["sentiment"]["sentiment"] == "neutral")
            
            video_sentiment = {
                "video_id": video_id,
                "title": video.get("title", ""),
                "analyzed_comments": analyzed_comments,
                "comment_count": len(analyzed_comments),
                "sentiment_distribution": {
                    "positive": positive_count / len(analyzed_comments) if analyzed_comments else 0,
                    "negative": negative_count / len(analyzed_comments) if analyzed_comments else 0,
                    "neutral": neutral_count / len(analyzed_comments) if analyzed_comments else 0
                },
                "average_score": sum(c["sentiment"]["score"] for c in analyzed_comments) / len(analyzed_comments) if analyzed_comments else 0
            }
            
            sentiment_results.append(video_sentiment)
            logger.info(f"비디오 '{video_id}' 감성 분석 완료 - "
                       f"긍정: {positive_count}, 부정: {negative_count}, 중립: {neutral_count}")
            
        except Exception as e:
            logger.error(f"비디오 '{video_id}' 감성 분석 중 오류 발생: {str(e)}")
    
    logger.info(f"감성 분석 완료 - 총 {total_comments}개 댓글 분석됨")
    
    # 전체 결과 통계 계산
    all_analyzed_comments = [comment for video in sentiment_results for comment in video["analyzed_comments"]]
    all_positive = sum(1 for c in all_analyzed_comments if c["sentiment"]["sentiment"] == "positive")
    all_negative = sum(1 for c in all_analyzed_comments if c["sentiment"]["sentiment"] == "negative")
    all_neutral = sum(1 for c in all_analyzed_comments if c["sentiment"]["sentiment"] == "neutral")
    
    return {
        "sentiment_results": sentiment_results,
        "total_analyzed": len(all_analyzed_comments),
        "sentiment_distribution": {
            "positive": all_positive / len(all_analyzed_comments) if all_analyzed_comments else 0,
            "negative": all_negative / len(all_analyzed_comments) if all_analyzed_comments else 0,
            "neutral": all_neutral / len(all_analyzed_comments) if all_analyzed_comments else 0
        },
        "average_score": sum(c["sentiment"]["score"] for c in all_analyzed_comments) / len(all_analyzed_comments) if all_analyzed_comments else 0
    }


@task(name="extract-keywords-task")
async def extract_keywords_task(sentiment_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    감성 분석된 댓글에서 키워드를 추출하는 태스크
    
    Args:
        sentiment_results: 감성 분석 결과
        
    Returns:
        키워드 추출 결과
    """
    logger = get_run_logger()
    logger.info("키워드 추출 시작")
    
    videos = sentiment_results.get("sentiment_results", [])
    if not videos:
        logger.warning("키워드 추출할 비디오 데이터가 없습니다.")
        return {"keywords": []}
    
    # 키워드 추출기 초기화
    extractor = KeywordExtractor()
    
    # 감성별 댓글 텍스트 모음
    positive_texts = []
    negative_texts = []
    neutral_texts = []
    
    for video in videos:
        for comment in video.get("analyzed_comments", []):
            text = comment.get("text_original", "")
            sentiment = comment.get("sentiment", {}).get("sentiment")
            
            if not text:
                continue
                
            if sentiment == "positive":
                positive_texts.append(text)
            elif sentiment == "negative":
                negative_texts.append(text)
            else:
                neutral_texts.append(text)
    
    logger.info(f"키워드 추출 대상 - 긍정: {len(positive_texts)}개, 부정: {len(negative_texts)}개, 중립: {len(neutral_texts)}개 댓글")
    
    # 감성별 키워드 추출
    try:
        positive_keywords = extractor.extract_keywords(" ".join(positive_texts), top_n=20) if positive_texts else []
        negative_keywords = extractor.extract_keywords(" ".join(negative_texts), top_n=20) if negative_texts else []
        neutral_keywords = extractor.extract_keywords(" ".join(neutral_texts), top_n=20) if neutral_texts else []
        
        # 전체 텍스트에서 키워드 추출
        all_texts = positive_texts + negative_texts + neutral_texts
        all_keywords = extractor.extract_keywords(" ".join(all_texts), top_n=30) if all_texts else []
        
        logger.info(f"키워드 추출 완료 - 전체: {len(all_keywords)}개, 긍정: {len(positive_keywords)}개, "
                  f"부정: {len(negative_keywords)}개, 중립: {len(neutral_keywords)}개 키워드")
        
        return {
            "keywords": {
                "all": all_keywords,
                "positive": positive_keywords,
                "negative": negative_keywords,
                "neutral": neutral_keywords
            }
        }
    
    except Exception as e:
        logger.error(f"키워드 추출 중 오류 발생: {str(e)}")
        return {"keywords": []}


@task(name="save-results-task")
async def save_results_task(
    collection_results: Dict[str, Any],
    sentiment_results: Dict[str, Any],
    keyword_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    분석 결과를 파일로 저장하는 태스크
    
    Args:
        collection_results: 수집 결과
        sentiment_results: 감성 분석 결과
        keyword_results: 키워드 추출 결과
        
    Returns:
        저장 결과 정보
    """
    logger = get_run_logger()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 분석 결과 통합
    analysis_result = {
        "timestamp": datetime.now().isoformat(),
        "collection_summary": {
            "total_videos": len(collection_results.get("videos", [])),
            "total_comments": collection_results.get("total_comments", 0)
        },
        "sentiment_analysis": {
            "total_analyzed": sentiment_results.get("total_analyzed", 0),
            "sentiment_distribution": sentiment_results.get("sentiment_distribution", {}),
            "average_score": sentiment_results.get("average_score", 0)
        },
        "keywords": keyword_results.get("keywords", {})
    }
    
    # 결과 저장
    output_file = DATA_DIR / f"analysis_result_{timestamp}.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"분석 결과가 {output_file}에 저장되었습니다.")
        
        # 최신 분석 결과를 analysis_result.json으로도 저장
        latest_file = DATA_DIR / "analysis_result.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "output_file": str(output_file),
            "latest_file": str(latest_file)
        }
    
    except Exception as e:
        logger.error(f"결과 저장 중 오류 발생: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@flow(name="youtube-analysis-pipeline")
async def youtube_analysis_pipeline(
    video_ids: List[str],
    max_comments: int = 100,
    run_sentiment_analysis: bool = True,
    run_keyword_extraction: bool = True,
    save_results: bool = True
) -> Dict[str, Any]:
    """
    YouTube 데이터 수집 및 분석 파이프라인
    
    Args:
        video_ids: 분석할 비디오 ID 목록
        max_comments: 비디오당 최대 수집 댓글 수
        run_sentiment_analysis: 감성 분석 수행 여부
        run_keyword_extraction: 키워드 추출 수행 여부
        save_results: 결과 저장 여부
        
    Returns:
        파이프라인 실행 결과
    """
    logger = get_run_logger()
    logger.info(f"YouTube 분석 파이프라인 시작 - {len(video_ids)}개 비디오")
    
    # 1. 비디오 ID 유효성 검사
    valid_ids = await check_video_ids(video_ids)
    
    if not valid_ids:
        logger.error("유효한 비디오 ID가 없습니다.")
        return {"error": "유효한 비디오 ID가 없습니다."}
    
    # 2. 데이터 수집
    collection_results = await collect_videos_task(valid_ids, max_comments)
    
    if not collection_results.get("videos"):
        logger.error("비디오 데이터 수집에 실패했습니다.")
        return {"error": "비디오 데이터 수집에 실패했습니다."}
    
    pipeline_results = {"collection": collection_results}
    
    # 3. 감성 분석
    if run_sentiment_analysis:
        sentiment_results = await analyze_sentiment_task(collection_results)
        pipeline_results["sentiment"] = sentiment_results
        
        # 4. 키워드 추출
        if run_keyword_extraction:
            keyword_results = await extract_keywords_task(sentiment_results)
            pipeline_results["keywords"] = keyword_results
            
            # 5. 결과 저장
            if save_results:
                save_results_output = await save_results_task(
                    collection_results, 
                    sentiment_results, 
                    keyword_results
                )
                pipeline_results["save_results"] = save_results_output
    
    logger.info("YouTube 분석 파이프라인 완료")
    return pipeline_results


def deploy_youtube_pipeline():
    """
    YouTube 분석 파이프라인을 배포합니다.
    """
    deployment = Deployment.build_from_flow(
        flow=youtube_analysis_pipeline,
        name="youtube-analysis-hourly",
        schedule=IntervalSchedule(interval=timedelta(hours=12)),
        tags=["youtube", "etl"],
        description="편의점 디저트 관련 YouTube 동영상을 수집하고 분석하는 파이프라인입니다."
    )
    deployment.apply()
    print(f"YouTube 분석 파이프라인이 배포되었습니다: {deployment.name}")


if __name__ == "__main__":
    # 파이프라인 직접 실행 또는 배포
    import asyncio
    
    # 예시 비디오 ID
    sample_video_ids = [
        "dQw4w9WgXcQ",  # Never Gonna Give You Up - Rick Astley
        "9bZkp7q19f0"   # Gangnam Style - PSY
    ]
    
    # 파이프라인 실행
    asyncio.run(youtube_analysis_pipeline(sample_video_ids))  