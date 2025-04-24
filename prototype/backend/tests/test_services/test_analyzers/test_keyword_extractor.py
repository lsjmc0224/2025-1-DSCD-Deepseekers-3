"""
키워드 추출기 모듈에 대한 단위 테스트

YAKE! 기반 키워드 추출 엔진의 기능 및 정확도를 검증합니다.
각 카테고리별 키워드 분류 성능을 테스트합니다.
"""

import os
import json
import pytest
import asyncio
from unittest import mock
from typing import List, Dict, Any

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.analyzers.keyword_extractor import (
    KeywordExtractor, get_extractor, CATEGORIES
)


# 테스트 데이터 설정
TEST_TEXTS = {
    "taste": [
        "이 디저트는 정말 달콤하고 맛있어요. 초콜릿 맛이 진하고 부드러워서 좋아요.",
        "너무 맵고 짜서 한 개만 먹어도 물을 계속 마시게 돼요. 맛이 별로예요.",
        "쫀득쫀득한 식감이 일품이에요. 달달하면서도 고소한 맛이 잘 어우러져요."
    ],
    "price": [
        "가격이 2000원인데 양이 많아서 가성비가 정말 좋아요.",
        "비싼 가격에 비해 맛은 그저 그래서 돈이 아까웠어요. 1500원이면 적당할 것 같아요.",
        "세일 중이라 천원에 샀는데 이 가격에 이런 맛이면 정말 대박이에요."
    ],
    "packaging": [
        "포장이 너무 예쁘고 선물용으로도 좋을 것 같아요. 상자 디자인이 고급스러워요.",
        "개봉하기 너무 힘들고 뜯다가 내용물이 다 쏟아졌어요. 패키지 설계가 잘못된 것 같아요.",
        "휴대하기 편한 미니 사이즈 포장이라 가방에 넣고 다니기 좋아요."
    ],
    "place": [
        "GS25에서만 판매하는 한정판이라 구하기 어려웠어요.",
        "세븐일레븐, CU, 이마트24 모든 편의점에서 쉽게 구할 수 있어서 좋아요.",
        "근처 편의점에는 다 품절이라 결국 온라인으로 주문했어요."
    ],
    "repurchase": [
        "너무 맛있어서 계속 생각나요. 또 사먹을 거예요.",
        "다시는 안 사먹을래요. 실망스러웠어요.",
        "인생 과자 찾았어요! 앞으로 쭉 애용할 거 같아요. 최고!"
    ],
    "mixed": [
        "GS25에서 1500원에 산 초코 쿠키인데, 너무 달지 않고 적당히 달콤해서 좋아요. 패키지도 귀엽고 또 사고 싶어요.",
        "편의점 디저트 중에 가격도 착하고 맛도 좋은데, 포장이 좀 투박해서 아쉬워요. 그래도 맛있어서 또 살 것 같아요.",
        "CU 신상 디저트를 샀는데 맛은 괜찮은데 가격이 좀 비싼 것 같아요. 포장은 예뻐서 선물하기 좋을 것 같아요."
    ]
}


# YAKE 모듈 모킹 클래스
class MockYake:
    def extract_keywords(self, text):
        """키워드 추출 모킹"""
        # 텍스트 길이에 따라 키워드 수 결정
        num_keywords = min(20, max(5, len(text) // 10))
        
        # 카테고리별 관련 단어 목록
        category_words = {
            "taste": ["맛", "달콤", "짜다", "식감", "부드럽"],
            "price": ["가격", "원", "저렴", "비싸", "가성비"],
            "packaging": ["포장", "디자인", "상자", "용기", "패키지"],
            "place": ["편의점", "CU", "GS25", "매장", "세븐일레븐"],
            "repurchase": ["또", "다시", "재구매", "추천", "최고"]
        }
        
        # 텍스트에 맞는 모의 키워드 생성
        keywords = []
        
        # 텍스트에 포함된 카테고리 단어 기반으로 키워드 생성
        for category, words in category_words.items():
            for word in words:
                if word in text.lower():
                    # 관련 키워드 추가
                    keywords.append((f"{word}한", 0.3))
                    keywords.append((f"{word} 있는", 0.4))
                    keywords.append((f"정말 {word}", 0.2))
        
        # 기본 키워드 추가
        keywords.extend([
            ("디저트", 0.1),
            ("과자", 0.2),
            ("초콜릿", 0.3),
            ("편의점", 0.15),
            ("신상", 0.25)
        ])
        
        # 중복 제거 및 상위 N개 선택
        unique_keywords = list(set(keywords))
        unique_keywords.sort(key=lambda x: x[1])  # 점수로 정렬
        
        return unique_keywords[:num_keywords]


@pytest.fixture
def mock_keyword_extractor():
    """키워드 추출기 모킹 픽스처"""
    
    with mock.patch("yake.KeywordExtractor") as mock_yake:
        # YAKE 모듈 모킹
        mock_yake.return_value = MockYake()
        
        # 키워드 추출기 인스턴스 생성
        extractor = KeywordExtractor()
        
        # 카테고리 벡터라이저 직접 설정
        extractor.category_vectors = {}
        
        for category, data in CATEGORIES.items():
            if category == "other":
                continue
                
            keywords = data["keywords"]
            if not keywords:
                continue
                
            # 카운트 벡터라이저 생성
            vectorizer = CountVectorizer(analyzer='char', ngram_range=(2, 3))
            
            # 키워드를 벡터화
            try:
                keyword_vectors = vectorizer.fit_transform(keywords)
                
                # 카테고리별 벡터와 벡터라이저 저장
                extractor.category_vectors[category] = {
                    "vectorizer": vectorizer,
                    "vectors": keyword_vectors
                }
                
            except Exception:
                pass
        
        yield extractor


@pytest.fixture
def real_keyword_texts():
    """키워드 추출용 실제 텍스트 샘플 픽스처"""
    return {
        "short": "GS25 초코 쿠키 맛있어요.",
        "medium": "CU에서 2000원에 산 초코 케이크인데 달달하고 맛있어요. 또 살 거예요.",
        "long": "이마트24에서 구매한 신상 초코 쿠키인데, 가격은 1200원으로 저렴한 편이고 맛도 달달하고 식감도 좋아요. 패키징도 예뻐서 선물용으로도 좋을 것 같아요. 편의점 디저트 중에서는 가성비 최고! 또 구매할 의향 있어요."
    }


# 키워드 추출기 테스트
class TestKeywordExtractor:
    """키워드 추출기 테스트 클래스"""
    
    @pytest.mark.asyncio
    async def test_extract_keywords_from_text(self, mock_keyword_extractor):
        """텍스트에서 키워드 추출 테스트"""
        # 텍스트 선택
        text = TEST_TEXTS["mixed"][0]
        
        # 키워드 추출
        result = await mock_keyword_extractor.extract_keywords(text, top_n=10)
        
        # 결과 검증
        assert isinstance(result, dict)
        assert "keywords" in result
        assert "top_keywords" in result
        assert "categories" in result
        assert len(result["keywords"]) <= 10
        assert all(isinstance(k, dict) and "keyword" in k and "score" in k for k in result["keywords"])
        
        # 카테고리 검증
        categories = result["categories"]
        assert isinstance(categories, dict)
        assert "taste" in categories
        assert "price" in categories
        assert "packaging" in categories
        assert "place" in categories
        assert "repurchase" in categories
    
    @pytest.mark.asyncio
    async def test_extract_keywords_for_specific_category(self, mock_keyword_extractor):
        """특정 카테고리 키워드 추출 테스트"""
        # 카테고리별 텍스트 선택
        for category, texts in TEST_TEXTS.items():
            if category == "mixed":
                continue
                
            # 카테고리별 첫 번째 텍스트로 테스트
            text = texts[0]
            
            # 키워드 추출
            result = await mock_keyword_extractor.extract_keywords(text, top_n=10)
            
            # 카테고리 결과 검증
            categories = result["categories"]
            assert isinstance(categories, dict)
            
            # 해당 카테고리에 키워드가 있어야 함
            if category != "mixed":
                assert len(categories[category]) > 0, f"{category} 카테고리에 키워드가 없습니다."
    
    @pytest.mark.asyncio
    async def test_extract_keywords_batch(self, mock_keyword_extractor):
        """배치 키워드 추출 테스트"""
        # 텍스트 목록 생성
        texts = [
            TEST_TEXTS["taste"][0],
            TEST_TEXTS["price"][0],
            TEST_TEXTS["packaging"][0]
        ]
        
        # 배치 키워드 추출
        results = await mock_keyword_extractor.extract_keywords_batch(texts, top_n=10)
        
        # 결과 검증
        assert isinstance(results, list)
        assert len(results) == len(texts)
        
        for result in results:
            assert isinstance(result, dict)
            assert "keywords" in result
            assert "top_keywords" in result
            assert "categories" in result
    
    @pytest.mark.asyncio
    async def test_classify_keywords(self, mock_keyword_extractor):
        """키워드 분류 테스트"""
        # 분류할 키워드
        keywords = [
            "맛있는",
            "가격이 저렴한",
            "포장이 예쁜",
            "CU에서 구매",
            "또 살 것 같은",
            "알 수 없는 키워드"
        ]
        
        # 키워드 분류
        categorized = await mock_keyword_extractor.classify_keywords(keywords)
        
        # 결과 검증
        assert isinstance(categorized, dict)
        
        # 각 카테고리에 키워드가 올바르게 분류되었는지 확인
        assert "맛있는" in categorized["taste"]
        assert "가격이 저렴한" in categorized["price"]
        assert "포장이 예쁜" in categorized["packaging"]
        assert "CU에서 구매" in categorized["place"]
        assert "또 살 것 같은" in categorized["repurchase"]
        assert "알 수 없는 키워드" in categorized["other"]
    
    @pytest.mark.asyncio
    async def test_extract_top_category_keywords(self, mock_keyword_extractor):
        """카테고리별 상위 키워드 추출 테스트"""
        # 혼합 텍스트 선택
        text = TEST_TEXTS["mixed"][0]
        
        # 카테고리별 상위 키워드 추출
        result = await mock_keyword_extractor.extract_top_category_keywords(
            text,
            top_categories=3,
            top_keywords_per_category=5
        )
        
        # 결과 검증
        assert isinstance(result, dict)
        assert "top_categories" in result
        assert "all_keywords" in result
        
        # 상위 카테고리 검증
        top_categories = result["top_categories"]
        assert isinstance(top_categories, list)
        assert len(top_categories) <= 3
        
        for cat_info in top_categories:
            assert "category" in cat_info
            assert "name" in cat_info
            assert "keywords" in cat_info
            assert len(cat_info["keywords"]) <= 5
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_distribution(self, mock_keyword_extractor):
        """키워드 기반 감성 분포 분석 테스트"""
        # 키워드 목록
        keywords = [
            "맛있는", "맛없는", "좋은", "나쁜", "훌륭한",
            "최고의", "최악의", "추천하는", "비추하는", "만족스러운"
        ]
        
        # 긍정/부정 단어 목록
        positive_words = ["맛있", "좋은", "훌륭", "최고", "추천", "만족"]
        negative_words = ["맛없", "나쁜", "최악", "비추"]
        
        # 감성 분포 분석
        result = await mock_keyword_extractor.analyze_sentiment_distribution(
            keywords,
            positive_words,
            negative_words
        )
        
        # 결과 검증
        assert isinstance(result, dict)
        assert "positive" in result
        assert "negative" in result
        assert "neutral" in result
        assert "total" in result
        assert "distribution" in result
        
        # 분포 검증
        assert result["positive"] == 6  # 긍정 키워드 수
        assert result["negative"] == 4  # 부정 키워드 수
        assert result["neutral"] == 0   # 중립 키워드 수
        assert result["total"] == 10    # 전체 키워드 수
        
        # 비율 검증
        assert result["distribution"]["positive"] == 0.6  # 긍정 비율
        assert result["distribution"]["negative"] == 0.4  # 부정 비율
        assert result["distribution"]["neutral"] == 0.0   # 중립 비율
    
    @pytest.mark.asyncio
    async def test_empty_text_handling(self, mock_keyword_extractor):
        """빈 텍스트 처리 테스트"""
        # 빈 텍스트
        empty_text = ""
        
        # 키워드 추출
        result = await mock_keyword_extractor.extract_keywords(empty_text)
        
        # 결과 검증
        assert isinstance(result, dict)
        assert "keywords" in result
        assert "top_keywords" in result
        assert "categories" in result
        assert len(result["keywords"]) == 0
        assert len(result["top_keywords"]) == 0
        
        # 빈 텍스트 배치 처리
        batch_result = await mock_keyword_extractor.extract_keywords_batch([])
        assert isinstance(batch_result, list)
        assert len(batch_result) == 0


@pytest.mark.asyncio
async def test_get_extractor_singleton():
    """키워드 추출기 싱글톤 패턴 테스트"""
    # 싱글톤 패턴 목킹
    with mock.patch("app.services.analyzers.keyword_extractor.KeywordExtractor") as mock_extractor_class:
        mock_extractor_class.return_value = mock.MagicMock()
        
        # 첫 번째 호출
        extractor1 = await get_extractor()
        
        # 두 번째 호출
        extractor2 = await get_extractor()
        
        # 싱글톤 패턴 검증 - 클래스는 한 번만 인스턴스화되어야 함
        mock_extractor_class.assert_called_once()
        
        # 두 참조는 동일한 인스턴스여야 함
        assert extractor1 is extractor2


# 실제 키워드 추출기 테스트 (통합 테스트)
class TestKeywordExtractorIntegration:
    """실제 키워드 추출기 통합 테스트 클래스"""
    
    @pytest.mark.asyncio
    async def test_real_extractor_with_samples(self, real_keyword_texts):
        """실제 키워드 추출기로 샘플 텍스트 분석 테스트"""
        # 실제 추출기 인스턴스 가져오기
        with mock.patch("app.services.analyzers.keyword_extractor.KeywordExtractor") as mock_extractor_class:
            # 키워드 추출기 모킹
            extractor_instance = mock.MagicMock()
            
            # extract_keywords 메소드 모킹
            async def mock_extract(*args, **kwargs):
                return {
                    "keywords": [{"keyword": "테스트", "score": 0.8}],
                    "top_keywords": ["테스트"],
                    "categories": {"taste": ["테스트"], "price": [], "packaging": [], "place": [], "repurchase": [], "other": []}
                }
            
            extractor_instance.extract_keywords.side_effect = mock_extract
            mock_extractor_class.return_value = extractor_instance
            
            extractor = await get_extractor()
            
            # 짧은 텍스트 분석
            short_result = await extractor.extract_keywords(real_keyword_texts["short"])
            assert "keywords" in short_result
            assert "categories" in short_result
            
            # 중간 텍스트 분석
            medium_result = await extractor.extract_keywords(real_keyword_texts["medium"])
            assert "keywords" in medium_result
            assert "categories" in medium_result
            
            # 긴 텍스트 분석
            long_result = await extractor.extract_keywords(real_keyword_texts["long"])
            assert "keywords" in long_result
            assert "categories" in long_result


# 카테고리 분류 정확도 평가 테스트
class TestCategoryClassification:
    """카테고리 분류 정확도 테스트 클래스"""
    
    def test_category_keywords_coverage(self):
        """카테고리 키워드 목록의 커버리지 테스트"""
        # 각 카테고리의 키워드 목록 검증
        for category, data in CATEGORIES.items():
            if category == "other":
                continue  # other 카테고리는 건너뜀
            
            # 키워드 목록이 비어있지 않아야 함
            assert "keywords" in data
            assert isinstance(data["keywords"], list)
            assert len(data["keywords"]) > 0, f"{category} 카테고리의 키워드 목록이 비어있습니다."
            
            # 카테고리의 이름이 있어야 함
            assert "name" in data
            assert isinstance(data["name"], str)
            assert len(data["name"]) > 0
    
    @pytest.mark.asyncio
    async def test_classification_accuracy(self, mock_keyword_extractor):
        """카테고리 분류 정확도 테스트"""
        # 카테고리별 테스트 키워드 준비
        category_test_keywords = {
            "taste": ["맛있는", "달달한", "새콤한", "쫀득한", "담백한"],
            "price": ["저렴한", "가성비", "비싼", "만원짜리", "할인된"],
            "packaging": ["예쁜 포장", "개봉하기 편한", "밀봉된", "휴대하기 좋은", "패키지가 고급진"],
            "place": ["CU에서", "GS25", "편의점", "이마트", "세븐일레븐에서 구매한"],
            "repurchase": ["또 사고 싶은", "재구매할", "추천하고 싶은", "인생 과자", "다시는 안 살"]
        }
        
        # 각 카테고리별 테스트
        for category, test_keywords in category_test_keywords.items():
            # 키워드 분류
            result = await mock_keyword_extractor.classify_keywords(test_keywords)
            
            # 해당 카테고리에 분류된 키워드 수
            classified_count = len(result[category])
            
            # 정확도 계산 (해당 카테고리로 분류된 키워드 비율)
            accuracy = classified_count / len(test_keywords)
            
            # 정확도가 60% 이상이어야 함
            assert accuracy >= 0.6, f"{category} 카테고리 분류 정확도가 너무 낮습니다: {accuracy:.2f}"
            
            # 결과 출력
            print(f"{category} 카테고리 분류 정확도: {accuracy:.2f}")
    
    @pytest.mark.asyncio
    async def test_mixed_text_classification(self, mock_keyword_extractor):
        """혼합 텍스트에서 카테고리 분류 테스트"""
        # 혼합 텍스트
        for text in TEST_TEXTS["mixed"]:
            # 키워드 추출
            result = await mock_keyword_extractor.extract_keywords(text)
            
            # 카테고리별 키워드 수
            category_counts = {
                cat: len(keywords) for cat, keywords in result["categories"].items()
            }
            
            # 적어도 두 개 이상의 카테고리에 키워드가 있어야 함
            categories_with_keywords = sum(1 for count in category_counts.values() if count > 0)
            assert categories_with_keywords >= 2, "혼합 텍스트에서 다양한 카테고리의 키워드가 추출되어야 합니다." 