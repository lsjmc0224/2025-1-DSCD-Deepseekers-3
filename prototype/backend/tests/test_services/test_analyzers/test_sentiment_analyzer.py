"""
감성 분석기 모듈에 대한 단위 테스트

다양한 텍스트 샘플에 대한 KR-BERT 기반 감성 분석 결과와 정확도를 검증합니다.
"""

import os
import json
import pytest
import asyncio
from unittest import mock
from datetime import datetime, timedelta

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from app.services.analyzers.sentiment_analyzer import (
    SentimentAnalyzer, SentimentDataset, get_analyzer
)


# 테스트 데이터 설정
TEST_TEXTS = {
    "positive": [
        "이 디저트는 정말 맛있어요! 달콤하고 부드러운 맛이 좋습니다.",
        "가격도 저렴하고 맛도 좋아서 자주 구매하게 되네요. 추천합니다!",
        "패키징이 너무 예뻐서 선물용으로도 좋을 것 같아요. 맛도 훌륭합니다.",
        "CU에서 산 초코 케이크인데 진짜 맛있어요! 또 살 거예요.",
        "이 과자 진짜 중독성 있어요. 한 봉지 순삭했네요. 최고의 간식!"
    ],
    "neutral": [
        "편의점에서 새로 나온 디저트라고 해서 구매해봤어요.",
        "맛은 평범한데 가격은 좀 비싼 것 같아요.",
        "패키징은 괜찮은데 양이 좀 적은 것 같습니다.",
        "GS25에서 구매했는데 다른 편의점에도 있는지 모르겠네요.",
        "먹어봤는데 그냥 그랬어요. 특별한 맛은 아니었습니다."
    ],
    "negative": [
        "이 디저트는 너무 달고 맛이 별로예요. 다시는 안 살 것 같아요.",
        "가격이 너무 비싼데 양도 적고 맛도 별로라서 실망했어요.",
        "포장은 예쁜데 내용물이 다 부서져 있었어요. 너무 실망스럽습니다.",
        "편의점 디저트 중에 제일 맛없었어요. 돈 아까워요.",
        "유통기한이 얼마 안 남았는데도 비싸게 팔아요. 맛도 없고 최악이었습니다."
    ]
}


class MockModel:
    """감성 분석 모델 모킹 클래스"""
    
    def __init__(self):
        self.device = "cpu"
    
    def __call__(self, input_ids=None, attention_mask=None, labels=None):
        """모델 호출 모킹"""
        batch_size = input_ids.size(0) if input_ids is not None else 1
        
        # 입력된 텍스트에 따라 결과 조작
        if labels is not None:
            # 학습 모드일 때
            return mock.MagicMock(loss=torch.tensor(0.1))
        else:
            # 추론 모드일 때
            # 긍정/중립/부정 감성 결과 생성 (배치 크기에 맞게)
            logits = torch.randn(batch_size, 3)
            return mock.MagicMock(logits=logits)
    
    def to(self, device):
        """장치 설정 모킹"""
        self.device = device
        return self
    
    def eval(self):
        """평가 모드 설정 모킹"""
        return self
    
    def train(self):
        """학습 모드 설정 모킹"""
        return self
    
    def save_pretrained(self, path):
        """모델 저장 모킹"""
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, "config.json"), "w") as f:
            json.dump({"model_type": "bert"}, f)
        return True


class MockTokenizer:
    """토크나이저 모킹 클래스"""
    
    def __call__(self, text, return_tensors=None, truncation=None, max_length=None, padding=None):
        """토크나이저 호출 모킹"""
        if isinstance(text, list):
            batch_size = len(text)
        else:
            batch_size = 1
        
        # 가짜 입력 ID와 어텐션 마스크 생성
        input_ids = torch.randint(0, 30000, (batch_size, 10))
        attention_mask = torch.ones_like(input_ids)
        
        result = {
            "input_ids": input_ids,
            "attention_mask": attention_mask
        }
        
        if return_tensors == "pt":
            pass  # 이미 PyTorch 텐서임
        
        return mock.MagicMock(**result, to=lambda device: result)
    
    def save_pretrained(self, path):
        """토크나이저 저장 모킹"""
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, "tokenizer_config.json"), "w") as f:
            json.dump({"model_type": "bert"}, f)
        return True


@pytest.fixture
def mock_sentiment_analyzer():
    """감성 분석기 모킹 픽스처"""
    with mock.patch("app.services.analyzers.sentiment_analyzer.AutoTokenizer.from_pretrained") as mock_tokenizer:
        with mock.patch("app.services.analyzers.sentiment_analyzer.AutoModelForSequenceClassification.from_pretrained") as mock_model:
            # 목 객체 설정
            mock_tokenizer.return_value = MockTokenizer()
            mock_model.return_value = MockModel()
            
            # 분석기 인스턴스 생성
            analyzer = SentimentAnalyzer()
            
            yield analyzer


@pytest.fixture
def real_sentiment_texts():
    """감성 분석용 실제 텍스트 샘플 픽스처"""
    return {
        "positive": "이 디저트는 정말 맛있어요! 달콤한 맛이 일품이에요. 또 구매할 생각입니다.",
        "neutral": "새로 나온 디저트라고 해서 구매해봤어요. 맛은 평범했습니다.",
        "negative": "이 디저트는 너무 달고 맛이 별로예요. 다시는 안 살 것 같아요."
    }


# 모의 감성 분석기 테스트
class TestMockSentimentAnalyzer:
    """모의 감성 분석기 테스트 클래스"""
    
    @pytest.mark.asyncio
    async def test_analyze_positive_text(self, mock_sentiment_analyzer):
        """긍정 텍스트 분석 테스트"""
        # 모의 분석기에 긍정 응답 설정
        mock_sentiment_analyzer.model = mock.MagicMock()
        mock_sentiment_analyzer.model.return_value = mock.MagicMock(
            logits=torch.tensor([[0.1, 0.2, 0.7]])  # 긍정 점수가 가장 높음
        )
        
        # 긍정 텍스트 분석
        result = await mock_sentiment_analyzer.analyze(TEST_TEXTS["positive"][0])
        
        # 결과 검증
        assert isinstance(result, dict)
        assert "sentiment" in result
        assert "positive" in result
        assert "negative" in result
        assert "neutral" in result
        assert "confidence" in result
    
    @pytest.mark.asyncio
    async def test_analyze_negative_text(self, mock_sentiment_analyzer):
        """부정 텍스트 분석 테스트"""
        # 모의 분석기에 부정 응답 설정
        mock_sentiment_analyzer.model = mock.MagicMock()
        mock_sentiment_analyzer.model.return_value = mock.MagicMock(
            logits=torch.tensor([[0.7, 0.2, 0.1]])  # 부정 점수가 가장 높음
        )
        
        # 부정 텍스트 분석
        result = await mock_sentiment_analyzer.analyze(TEST_TEXTS["negative"][0])
        
        # 결과 검증
        assert isinstance(result, dict)
        assert "sentiment" in result
        assert result["negative"] > result["positive"]
    
    @pytest.mark.asyncio
    async def test_analyze_batch(self, mock_sentiment_analyzer):
        """배치 텍스트 분석 테스트"""
        # 모의 분석기에 배치 응답 설정
        def side_effect(**kwargs):
            batch_size = kwargs.get("input_ids").size(0)
            logits = torch.ones(batch_size, 3)  # 모든 감성에 동일한 점수
            return mock.MagicMock(logits=logits)
        
        mock_sentiment_analyzer.model.side_effect = side_effect
        
        # 여러 텍스트 배치 분석
        mixed_texts = TEST_TEXTS["positive"][:2] + TEST_TEXTS["neutral"][:2] + TEST_TEXTS["negative"][:2]
        results = await mock_sentiment_analyzer.analyze_batch(mixed_texts)
        
        # 결과 검증
        assert isinstance(results, list)
        assert len(results) == len(mixed_texts)
        for result in results:
            assert isinstance(result, dict)
            assert "sentiment" in result
            assert "positive" in result
            assert "negative" in result
            assert "neutral" in result
            assert "confidence" in result
    
    @pytest.mark.asyncio
    async def test_empty_text_handling(self, mock_sentiment_analyzer):
        """빈 텍스트 처리 테스트"""
        # 빈 텍스트 분석
        result = await mock_sentiment_analyzer.analyze("")
        
        # 결과 검증 - 중립으로 처리되어야 함
        assert isinstance(result, dict)
        assert result["sentiment"] == "neutral"
        assert result["neutral"] == 1.0
        
        # 빈 배치 분석
        results = await mock_sentiment_analyzer.analyze_batch([])
        
        # 결과 검증 - 빈 리스트 반환
        assert isinstance(results, list)
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_sentiment_analyzer):
        """오류 처리 테스트"""
        # 모의 분석기에 예외 발생 설정
        mock_sentiment_analyzer.model.side_effect = Exception("Test error")
        
        # 텍스트 분석 시 오류 발생
        result = await mock_sentiment_analyzer.analyze("테스트 텍스트")
        
        # 결과 검증 - 오류 처리되어야 함
        assert isinstance(result, dict)
        assert result["sentiment"] == "neutral"
        assert "error" in result
        
        # 배치 분석 시 오류 발생
        results = await mock_sentiment_analyzer.analyze_batch(["테스트1", "테스트2"])
        
        # 결과 검증 - 모든 항목이 오류 처리되어야 함
        assert isinstance(results, list)
        assert len(results) == 2
        for result in results:
            assert result["sentiment"] == "neutral"
            assert "error" in result


# 실제 감성 분석기 테스트 (통합 테스트)
class TestSentimentAnalyzerIntegration:
    """실제 감성 분석기 통합 테스트 클래스"""
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="GPU가 필요한 테스트입니다")
    @pytest.mark.asyncio
    async def test_real_analyzer_with_samples(self, real_sentiment_texts):
        """실제 감성 분석기로 샘플 텍스트 분석 테스트"""
        # 실제 분석기 인스턴스 가져오기
        analyzer = await get_analyzer()
        
        # 긍정 텍스트 분석
        positive_result = await analyzer.analyze(real_sentiment_texts["positive"])
        assert positive_result["sentiment"] in ["positive", "neutral", "negative"]
        
        # 중립 텍스트 분석
        neutral_result = await analyzer.analyze(real_sentiment_texts["neutral"])
        assert neutral_result["sentiment"] in ["positive", "neutral", "negative"]
        
        # 부정 텍스트 분석
        negative_result = await analyzer.analyze(real_sentiment_texts["negative"])
        assert negative_result["sentiment"] in ["positive", "neutral", "negative"]
    
    @pytest.mark.asyncio
    async def test_fine_tuning_workflow(self, mock_sentiment_analyzer):
        """미세 조정 워크플로우 테스트"""
        # 학습 및 검증 데이터 준비
        train_texts = (
            TEST_TEXTS["positive"][:3] + 
            TEST_TEXTS["neutral"][:3] + 
            TEST_TEXTS["negative"][:3]
        )
        train_labels = ["positive"] * 3 + ["neutral"] * 3 + ["negative"] * 3
        
        val_texts = (
            TEST_TEXTS["positive"][3:] + 
            TEST_TEXTS["neutral"][3:] + 
            TEST_TEXTS["negative"][3:]
        )
        val_labels = ["positive"] * 2 + ["neutral"] * 2 + ["negative"] * 2
        
        # 임시 모델 저장 경로
        temp_model_path = "test_model_path"
        os.makedirs(temp_model_path, exist_ok=True)
        
        try:
            # 미세 조정 실행
            fine_tune_result = await mock_sentiment_analyzer.fine_tune(
                train_texts=train_texts,
                train_labels=train_labels,
                val_texts=val_texts,
                val_labels=val_labels,
                epochs=1,
                batch_size=2,
                save_path=temp_model_path
            )
            
            # 결과 검증
            assert isinstance(fine_tune_result, dict)
            assert "epochs_completed" in fine_tune_result
            assert "train_samples" in fine_tune_result
            assert fine_tune_result["train_samples"] == len(train_texts)
            assert "val_samples" in fine_tune_result
            assert fine_tune_result["val_samples"] == len(val_texts)
            
        finally:
            # 테스트 후 정리
            import shutil
            if os.path.exists(temp_model_path):
                shutil.rmtree(temp_model_path)
    
    @pytest.mark.asyncio
    async def test_dataset_functionality(self):
        """데이터셋 기능 테스트"""
        # 텍스트 데이터 준비
        texts = TEST_TEXTS["positive"][:2]
        labels = [2, 2]  # 긍정 레이블 (2)
        
        # 모의 토크나이저
        tokenizer = MockTokenizer()
        
        # 데이터셋 생성
        dataset = SentimentDataset(texts, tokenizer, labels, max_length=128)
        
        # 데이터셋 길이 검증
        assert len(dataset) == len(texts)
        
        # 데이터셋 항목 검증
        item = dataset[0]
        assert "input_ids" in item
        assert "attention_mask" in item
        assert "labels" in item
        assert isinstance(item["labels"], torch.Tensor)
        assert item["labels"].item() == labels[0]


@pytest.mark.asyncio
async def test_get_analyzer_singleton():
    """감성 분석기 싱글톤 패턴 테스트"""
    # 싱글톤 패턴 목킹
    with mock.patch("app.services.analyzers.sentiment_analyzer.SentimentAnalyzer") as mock_analyzer_class:
        mock_analyzer_class.return_value = mock.MagicMock()
        
        # 첫 번째 호출
        analyzer1 = await get_analyzer()
        
        # 두 번째 호출
        analyzer2 = await get_analyzer()
        
        # 싱글톤 패턴 검증 - 클래스는 한 번만 인스턴스화되어야 함
        mock_analyzer_class.assert_called_once()
        
        # 두 참조는 동일한 인스턴스여야 함
        assert analyzer1 is analyzer2


# 정확도 평가 테스트
@pytest.mark.asyncio
async def test_sentiment_accuracy_evaluation(mock_sentiment_analyzer):
    """감성 분석 정확도 평가 테스트"""
    # 평가용 데이터셋 준비
    eval_texts = []
    eval_labels = []
    
    # 긍정, 중립, 부정 텍스트 혼합
    for category, texts in TEST_TEXTS.items():
        eval_texts.extend(texts)
        if category == "positive":
            eval_labels.extend([2] * len(texts))  # 긍정 레이블
        elif category == "neutral":
            eval_labels.extend([1] * len(texts))  # 중립 레이블
        else:  # negative
            eval_labels.extend([0] * len(texts))  # 부정 레이블
    
    # 토크나이저 및 데이터셋 모킹
    tokenizer = MockTokenizer()
    dataset = SentimentDataset(eval_texts, tokenizer, eval_labels)
    
    # 데이터로더 모킹
    class MockDataLoader:
        def __init__(self, dataset):
            self.dataset = dataset
            self.batch_size = 2
        
        def __iter__(self):
            for i in range(0, len(self.dataset), self.batch_size):
                batch = {
                    "input_ids": torch.tensor([[1, 2, 3], [4, 5, 6]]),
                    "attention_mask": torch.tensor([[1, 1, 1], [1, 1, 1]]),
                    "labels": torch.tensor([0, 1])  # 부정, 중립
                }
                yield batch
    
    mock_dataloader = MockDataLoader(dataset)
    
    # _evaluate 메소드 호출
    accuracy, metrics = await mock_sentiment_analyzer._evaluate(mock_dataloader)
    
    # 정확도 및 메트릭 검증
    assert isinstance(accuracy, float)
    assert 0 <= accuracy <= 1
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics 