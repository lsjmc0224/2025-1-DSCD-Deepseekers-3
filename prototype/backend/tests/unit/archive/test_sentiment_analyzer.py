"""
감성 분석기 단위 테스트

감성 분석 모듈에 대한 단위 테스트를 제공합니다.
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# 상위 디렉토리 추가하여 app 모듈 import 가능하게 함
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 테스트할 모듈 가져오기
from app.services.analysis.sentiment_analyzer import SentimentAnalyzer
from app.services.analysis.sentiment_analyzer_simple import SimpleSentimentAnalyzer


class TestSimpleSentimentAnalyzer(unittest.TestCase):
    """간단한 감성 분석기 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.analyzer = SimpleSentimentAnalyzer()
        
    def test_analyze_positive_text(self):
        """긍정적 텍스트 분석 테스트"""
        text = "이 디저트는 정말 맛있어요. 좋아요!"
        result = self.analyzer.analyze(text)
        
        self.assertEqual(result["sentiment"], "positive")
        self.assertGreater(result["score"], 0.5)
        self.assertTrue(len(result["positive_words"]) > 0)
        self.assertIn("맛있어요", result["positive_words"])
        self.assertIn("좋아요", result["positive_words"])
        
    def test_analyze_negative_text(self):
        """부정적 텍스트 분석 테스트"""
        text = "이 디저트는 맛이 없어요. 실망스러워요."
        result = self.analyzer.analyze(text)
        
        self.assertEqual(result["sentiment"], "negative")
        self.assertLess(result["score"], 0.5)
        self.assertTrue(len(result["negative_words"]) > 0)
        self.assertIn("없어요", result["negative_words"])
        self.assertIn("실망스러워요", result["negative_words"])
        
    def test_analyze_neutral_text(self):
        """중립적 텍스트 분석 테스트"""
        text = "이 디저트는 초콜릿 맛이고 가격은 2000원입니다."
        result = self.analyzer.analyze(text)
        
        self.assertEqual(result["sentiment"], "neutral")
        self.assertTrue(0.4 <= result["score"] <= 0.6)
        
    def test_empty_text(self):
        """빈 텍스트 분석 테스트"""
        text = ""
        result = self.analyzer.analyze(text)
        
        self.assertEqual(result["sentiment"], "neutral")
        self.assertEqual(result["score"], 0.5)
        self.assertEqual(result["positive_words"], [])
        self.assertEqual(result["negative_words"], [])


class TestSentimentAnalyzer(unittest.TestCase):
    """감성 분석기 테스트 클래스"""
    
    @patch('app.services.analysis.sentiment_analyzer.pipeline')
    def setUp(self, mock_pipeline):
        """테스트 설정"""
        # Mock transformer 파이프라인 설정
        self.mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = self.mock_pipeline_instance
        
        # 감성 분석기 초기화
        self.analyzer = SentimentAnalyzer()
        
    def test_analyze_with_transformer(self):
        """Transformer 모델을 사용한 감성 분석 테스트"""
        # Mock 응답 설정
        self.mock_pipeline_instance.return_value = [
            {'label': 'positive', 'score': 0.95}
        ]
        
        # 테스트 실행
        text = "이 디저트는 정말 맛있어요!"
        result = self.analyzer.analyze(text)
        
        # 검증
        self.assertEqual(result["sentiment"], "positive")
        self.assertEqual(result["score"], 0.95)
        
    def test_get_sentiment_words(self):
        """감성 단어 추출 테스트"""
        # 긍정 단어, 부정 단어 목록 설정
        self.analyzer.positive_words = ["좋은", "맛있는", "훌륭한"]
        self.analyzer.negative_words = ["나쁜", "맛없는", "실망스러운"]
        
        # 테스트 문장
        text = "이 디저트는 맛있는 초콜릿이 들어있어 좋은 맛이지만, 가격이 비싸서 실망스러운 부분도 있어요."
        
        # 감성 단어 추출
        positive_words, negative_words = self.analyzer.get_sentiment_words(text)
        
        # 검증
        self.assertIn("맛있는", positive_words)
        self.assertIn("좋은", positive_words)
        self.assertIn("실망스러운", negative_words)
        
    def test_analyze_comment_batch(self):
        """댓글 배치 분석 테스트"""
        # Mock 응답 설정
        self.mock_pipeline_instance.return_value = [
            {'label': 'positive', 'score': 0.9},
            {'label': 'negative', 'score': 0.8}
        ]
        
        # 테스트 실행
        comments = [
            {"text_original": "이 디저트는 정말 맛있어요!"},
            {"text_original": "가격이 너무 비싸고 맛도 별로에요."}
        ]
        
        results = self.analyzer.analyze_comments(comments)
        
        # 검증
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["sentiment"]["sentiment"], "positive")
        self.assertEqual(results[1]["sentiment"]["sentiment"], "negative")


if __name__ == '__main__':
    unittest.main() 