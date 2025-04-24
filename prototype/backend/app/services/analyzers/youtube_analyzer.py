import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..collectors.youtube_collector import collect_video_data, save_video_data
from ..processors.text_processor import TextProcessor
from .sentiment_analyzer import SimpleSentimentAnalyzer

class YouTubeAnalyzer:
    """
    YouTube 데이터 분석기.
    비디오, 댓글, 자막 등 YouTube 데이터를 종합적으로 분석합니다.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        YouTube 분석기를 초기화합니다.
        
        Args:
            api_key: YouTube API 키 (기본값: 환경 변수)
        """
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY", "")
        self.text_processor = TextProcessor()
        self.sentiment_analyzer = SimpleSentimentAnalyzer()
    
    def collect_data(self, video_id_or_url: str, include_comments: bool = True, 
                    include_transcript: bool = True, include_channel: bool = True,
                    max_comments: int = 100) -> Dict[str, Any]:
        """
        YouTube 데이터를 수집합니다.
        
        Args:
            video_id_or_url: YouTube 비디오 ID 또는 URL
            include_comments: 댓글 포함 여부
            include_transcript: 자막 포함 여부
            include_channel: 채널 정보 포함 여부
            max_comments: 수집할 최대 댓글 수
            
        Returns:
            수집된 데이터
        """
        return collect_video_data(
            video_id_or_url=video_id_or_url,
            include_comments=include_comments,
            include_transcript=include_transcript,
            include_channel=include_channel,
            max_comments=max_comments,
            api_key=self.api_key
        )
    
    def analyze_video(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        수집된 YouTube 비디오 데이터를 분석합니다.
        
        Args:
            video_data: 수집된 비디오 데이터
            
        Returns:
            분석 결과
        """
        if "error" in video_data:
            return {
                "error": video_data["error"],
                "timestamp": datetime.now().isoformat()
            }
        
        # 타임스탬프
        timestamp = datetime.now().isoformat()
        
        # 메타데이터
        metadata = {
            "video_id": video_data.get("video", {}).get("id", ""),
            "title": video_data.get("video", {}).get("title", ""),
            "channel_title": video_data.get("video", {}).get("channel_title", ""),
            "published_at": video_data.get("video", {}).get("published_at", ""),
            "view_count": video_data.get("video", {}).get("view_count", 0),
            "like_count": video_data.get("video", {}).get("like_count", 0),
            "comment_count": video_data.get("video", {}).get("comment_count", 0),
            "duration_seconds": video_data.get("video", {}).get("duration_seconds", 0)
        }
        
        # 결과 초기화
        result = {
            "timestamp": timestamp,
            "metadata": metadata,
            "sentiment_analysis": {},
            "keyword_analysis": {},
            "channel_info": {}
        }
        
        # 채널 정보
        if "channel" in video_data:
            channel = video_data["channel"]
            result["channel_info"] = {
                "title": channel.get("title", ""),
                "subscriber_count": channel.get("subscriber_count", 0),
                "video_count": channel.get("video_count", 0),
                "view_count": channel.get("view_count", 0)
            }
        
        # 댓글 분석
        if "comments" in video_data:
            comments = video_data["comments"]
            
            # 감성 분석
            sentiment_results = self.sentiment_analyzer.analyze_comments(comments)
            
            # 텍스트 및 키워드 분석
            text_analysis = self.text_processor.analyze_comments(comments)
            
            result["sentiment_analysis"] = {
                "distribution": sentiment_results.get("sentiment_distribution", {}),
                "average_score": sentiment_results.get("average_score", 0.0),
                "comment_count": len(comments)
            }
            
            result["keyword_analysis"] = {
                "keywords": text_analysis.get("keywords", []),
                "categorized_keywords": text_analysis.get("categorized_keywords", {})
            }
        
        # 자막 분석
        if "transcript" in video_data:
            transcript_analysis = self.text_processor.analyze_transcript(video_data["transcript"])
            
            # 자막이 있을 경우 키워드 분석에 추가
            existing_keywords = set(kw[0] for kw in result.get("keyword_analysis", {}).get("keywords", []))
            
            transcript_keywords = transcript_analysis.get("keywords", [])
            filtered_transcript_keywords = [kw for kw in transcript_keywords if kw[0] not in existing_keywords]
            
            # 기존 키워드와 자막 키워드 병합
            combined_keywords = result.get("keyword_analysis", {}).get("keywords", [])[:]
            combined_keywords.extend(filtered_transcript_keywords)
            
            # 키워드 다시 분류
            categorized_combined = self.text_processor.categorize_keywords(combined_keywords)
            
            result["transcript_analysis"] = {
                "sentence_count": transcript_analysis.get("sentence_count", 0),
                "transcript_length": transcript_analysis.get("transcript_length", 0),
                "keywords": transcript_analysis.get("keywords", [])
            }
            
            # 키워드 분석 업데이트
            result["keyword_analysis"] = {
                "keywords": combined_keywords[:30],  # 상위 30개만 유지
                "categorized_keywords": categorized_combined
            }
        
        return result
    
    def analyze(self, video_id_or_url: str, save_results: bool = False, 
               output_dir: str = "data") -> Dict[str, Any]:
        """
        YouTube 비디오를 수집하고 분석합니다.
        
        Args:
            video_id_or_url: YouTube 비디오 ID 또는 URL
            save_results: 결과 저장 여부
            output_dir: 결과를 저장할 디렉토리
            
        Returns:
            분석 결과
        """
        # 데이터 수집
        video_data = self.collect_data(video_id_or_url)
        
        # 수집된 데이터 저장 (옵션)
        if save_results:
            video_id = video_data.get("video", {}).get("id", "unknown")
            raw_data_filename = f"{video_id}_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_video_data(video_data, output_dir, raw_data_filename)
        
        # 데이터 분석
        analysis_result = self.analyze_video(video_data)
        
        # 분석 결과 저장 (옵션)
        if save_results:
            video_id = analysis_result.get("metadata", {}).get("video_id", "unknown")
            analysis_filename = f"{video_id}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, analysis_filename)
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        
        return analysis_result
    
    def save_for_visualization(self, analysis_result: Dict[str, Any], 
                             output_dir: str = "frontend/public/data") -> str:
        """
        분석 결과를 시각화를 위한 형식으로 저장합니다.
        
        Args:
            analysis_result: 분석 결과
            output_dir: 출력 디렉토리
            
        Returns:
            저장된 파일 경로
        """
        os.makedirs(output_dir, exist_ok=True)
        
        video_id = analysis_result.get("metadata", {}).get("video_id", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 최신 분석 파일용 데이터 생성
        visualization_data = {
            "metadata": analysis_result.get("metadata", {}),
            "sentiment_analysis": analysis_result.get("sentiment_analysis", {}),
            "keyword_analysis": {
                "keywords": [{"word": kw[0], "score": kw[1]} for kw in analysis_result.get("keyword_analysis", {}).get("keywords", [])[:20]],
                "categories": {}
            },
            "channel_info": analysis_result.get("channel_info", {})
        }
        
        # 카테고리별 키워드
        for category, keywords in analysis_result.get("keyword_analysis", {}).get("categorized_keywords", {}).items():
            visualization_data["keyword_analysis"]["categories"][category] = [
                {"word": kw[0], "score": kw[1]} for kw in keywords[:5]
            ]
        
        # 시각화 데이터 저장
        filename = f"{video_id}_viz_{timestamp}.json"
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(visualization_data, f, ensure_ascii=False, indent=2)
        
        # 또한 최신 파일로 복사
        latest_filename = f"{video_id}_latest.json"
        latest_path = os.path.join(output_dir, latest_filename)
        
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(visualization_data, f, ensure_ascii=False, indent=2)
        
        return file_path 