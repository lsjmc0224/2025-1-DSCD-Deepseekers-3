"""
간단한 감성 분석기 모듈.
"""
from typing import Dict, List, Any

class SimpleSentimentAnalyzer:
    """
    매우 간단한 감성 분석기.
    미리 정의된 긍정/부정 단어 목록을 사용하여 텍스트의 감성을 분석합니다.
    """
    
    def __init__(self):
        """간단한 감성 분석기를 초기화합니다."""
        # 기본 감성 단어 목록
        self.positive_words = [
            "좋아요", "멋져요", "훌륭해요", "최고", "감사", "행복", "아름다운", 
            "맛있", "추천", "최애", "존맛", "완벽", "만족", "좋다", "좋았", "좋은"
        ]
        
        self.negative_words = [
            "별로", "싫어요", "최악", "실망", "후회", "불만", "불편", "나쁜", 
            "비추", "형편없", "안좋", "다신안", "그냥", "보통", "그저그럼"
        ]
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        텍스트의 감성을 분석합니다.
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            감성 분석 결과 (positive, negative, neutral)
        """
        if not text:
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "positive_count": 0,
                "negative_count": 0
            }
        
        text = text.lower()
        
        # 감성 단어 카운트
        positive_count = sum(1 for word in self.positive_words if word in text)
        negative_count = sum(1 for word in self.negative_words if word in text)
        
        # 감성 점수 계산 (-1.0 ~ 1.0)
        total_count = positive_count + negative_count
        
        if total_count == 0:
            score = 0.0
            sentiment = "neutral"
        else:
            score = (positive_count - negative_count) / total_count
            
            if score > 0.1:
                sentiment = "positive"
            elif score < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "score": round(score, 2),
            "positive_count": positive_count,
            "negative_count": negative_count
        }
    
    def analyze_comments(self, comments: List[Dict[str, Any]], 
                        text_key: str = "text_original") -> Dict[str, Any]:
        """
        댓글 목록의 감성을 분석합니다.
        
        Args:
            comments: 댓글 목록 (각 댓글은 딕셔너리 형태)
            text_key: 댓글 텍스트가 저장된 키 이름
            
        Returns:
            전체 댓글에 대한 감성 분석 요약 및 각 댓글별 감성
        """
        if not comments:
            return {
                "sentiment_distribution": {
                    "positive": 0.0,
                    "neutral": 0.0,
                    "negative": 0.0
                },
                "average_score": 0.0,
                "comment_count": 0,
                "comments": []
            }
        
        analyzed_comments = []
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        total_score = 0.0
        
        for comment in comments:
            if text_key not in comment:
                continue
                
            text = comment[text_key]
            sentiment_result = self.analyze(text)
            
            # 원본 댓글에 감성 분석 결과 추가
            comment_with_sentiment = comment.copy()
            comment_with_sentiment["sentiment"] = sentiment_result
            
            analyzed_comments.append(comment_with_sentiment)
            sentiment_counts[sentiment_result["sentiment"]] += 1
            total_score += sentiment_result["score"]
        
        comment_count = len(analyzed_comments)
        
        if comment_count == 0:
            return {
                "sentiment_distribution": {
                    "positive": 0.0,
                    "neutral": 0.0,
                    "negative": 0.0
                },
                "average_score": 0.0,
                "comment_count": 0,
                "comments": []
            }
        
        # 감성 분포 계산
        sentiment_distribution = {
            "positive": round(sentiment_counts["positive"] / comment_count, 2),
            "neutral": round(sentiment_counts["neutral"] / comment_count, 2),
            "negative": round(sentiment_counts["negative"] / comment_count, 2)
        }
        
        # 평균 감성 점수
        average_score = round(total_score / comment_count, 2)
        
        return {
            "sentiment_distribution": sentiment_distribution,
            "average_score": average_score,
            "comment_count": comment_count,
            "comments": analyzed_comments
        } 