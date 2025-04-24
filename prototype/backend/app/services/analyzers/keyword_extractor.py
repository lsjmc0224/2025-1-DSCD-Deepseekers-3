"""
YAKE! 기반 키워드 추출 엔진

텍스트에서 중요 키워드를 추출하고 카테고리별로 분류하는 모듈입니다.
맛, 가격, 패키징, 판매처, 재구매 의향 등의 카테고리로 키워드를 분류합니다.
"""

import re
import json
import logging
import asyncio
from typing import Dict, List, Any, Tuple, Set, Optional
from collections import defaultdict

import yake
from konlpy.tag import Komoran
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import settings

logger = logging.getLogger(__name__)

# 카테고리 정의
CATEGORIES = {
    "taste": {
        "name": "맛",
        "keywords": [
            "맛", "맛있", "맛없", "달콤", "고소", "짜", "싱겁", "씁쓸", "신맛", "단맛", "쓴맛", 
            "짠맛", "매콤", "맵", "부드럽", "식감", "촉촉", "바삭", "쫀득", "달달", "새콤", 
            "떫", "담백", "고소", "풍미", "향", "맛없", "맛있어", "맛있네", "맛집", "맛보", 
            "맛남", "맛나", "맛난", "풍부", "특이", "독특"
        ]
    },
    "price": {
        "name": "가격",
        "keywords": [
            "가격", "원", "비싸", "저렴", "싸", "값", "쌈", "가성비", "비싸", "비싸네", "가성비", 
            "값어치", "돈값", "가격 대비", "합리적", "무료", "할인", "세일", "프로모션", "저렴", 
            "예산", "원", "만원", "천원", "백원"
        ]
    },
    "packaging": {
        "name": "패키징",
        "keywords": [
            "포장", "패키지", "디자인", "용기", "상자", "모양", "생김새", "간편", "편리", "뚜껑", 
            "비닐", "봉지", "보관", "유통기한", "밀봉", "개봉", "소포장", "대용량", "미니", 
            "휴대", "들고 다니", "꺼내", "열기", "밀폐", "신선"
        ]
    },
    "place": {
        "name": "판매처",
        "keywords": [
            "편의점", "CU", "GS25", "세븐일레븐", "이마트24", "미니스톱", "마트", "슈퍼", 
            "대형마트", "이마트", "홈플러스", "롯데마트", "코스트코", "백화점", "온라인", 
            "쿠팡", "마켓컬리", "SSG", "배달", "품절", "구입", "구매", "살", "팔", 
            "매장", "진열", "재고", "한정판"
        ]
    },
    "repurchase": {
        "name": "재구매 의향",
        "keywords": [
            "또", "재구매", "또 사", "또 먹", "계속", "다시", "추천", "비추", "추천해", 
            "추천합니다", "안 사", "재구매", "다음에", "다시 사", "또 구매", "또 찾", 
            "습관성", "중독성", "자꾸", "생각나", "안 살", "인생템", "최고", "진리", 
            "찐", "꿀맛", "최애", "강추", "혐", "노맛"
        ]
    },
    "other": {
        "name": "기타",
        "keywords": []
    }
}


class KeywordExtractor:
    """
    YAKE! 알고리즘 기반 키워드 추출 및 분류 엔진
    """
    
    def __init__(
        self,
        custom_categories: Optional[Dict[str, Dict[str, Any]]] = None,
        language: str = "ko",
        max_ngram_size: int = 2,
        deduplication_threshold: float = 0.9,
        num_keywords: int = 20
    ):
        """
        KeywordExtractor 초기화
        
        Args:
            custom_categories: 사용자 정의 카테고리 (None이면 기본값 사용)
            language: 언어 설정 (기본값: 한국어)
            max_ngram_size: 최대 n-gram 크기
            deduplication_threshold: 중복 제거 임계값
            num_keywords: 추출할 키워드 수
        """
        self.language = language
        self.max_ngram_size = max_ngram_size
        self.deduplication_threshold = deduplication_threshold
        self.num_keywords = num_keywords
        
        # 카테고리 설정
        self.categories = custom_categories or CATEGORIES
        
        # 형태소 분석기 초기화
        self.komoran = Komoran()
        
        # YAKE 추출기 초기화
        self.kw_extractor = yake.KeywordExtractor(
            lan=self.language,
            n=self.max_ngram_size,
            dedupLim=self.deduplication_threshold,
            top=self.num_keywords,
            features=None
        )
        
        # 카테고리별 키워드 벡터라이저 초기화
        self._initialize_category_vectorizers()
        
        logger.info("키워드 추출 엔진 초기화 완료")
    
    def _initialize_category_vectorizers(self):
        """
        카테고리별 벡터라이저 초기화
        """
        self.category_vectors = {}
        
        for category, data in self.categories.items():
            if category == "other":
                continue  # 기타 카테고리는 건너뜀
                
            # 카테고리 키워드에서 벡터 생성
            keywords = data["keywords"]
            if not keywords:
                continue
                
            # 카운트 벡터라이저 생성
            vectorizer = CountVectorizer(analyzer='char', ngram_range=(2, 3))
            
            # 키워드를 벡터화
            try:
                keyword_vectors = vectorizer.fit_transform(keywords)
                
                # 카테고리별 벡터와 벡터라이저 저장
                self.category_vectors[category] = {
                    "vectorizer": vectorizer,
                    "vectors": keyword_vectors
                }
                
            except Exception as e:
                logger.error(f"카테고리 '{category}' 벡터화 중 오류 발생: {str(e)}")
    
    async def extract_keywords(
        self, 
        text: str,
        top_n: int = 20,
        classify: bool = True
    ) -> Dict[str, Any]:
        """
        텍스트에서 키워드를 추출하고 카테고리별로 분류합니다.
        
        Args:
            text: 키워드를 추출할 텍스트
            top_n: 추출할 상위 키워드 수
            classify: 카테고리별 분류 여부
            
        Returns:
            Dict[str, Any]: 추출된 키워드 정보
        """
        if not text or len(text.strip()) == 0:
            return {
                "keywords": [],
                "categories": {},
                "top_keywords": []
            }
        
        try:
            # YAKE를 사용하여 키워드 추출
            keywords = self.kw_extractor.extract_keywords(text)
            
            # 점수 기준으로 정렬 (YAKE에서는 점수가 낮을수록 중요)
            keywords.sort(key=lambda x: x[1])
            
            # 상위 N개 키워드 선택
            top_keywords = keywords[:top_n]
            
            # 결과 형식 변환
            keyword_results = [
                {"keyword": kw, "score": 1.0 - score} for kw, score in top_keywords
            ]
            
            result = {
                "keywords": keyword_results,
                "top_keywords": [kw for kw, _ in top_keywords]
            }
            
            # 카테고리별 분류
            if classify:
                categorized = await self.classify_keywords(result["top_keywords"])
                result["categories"] = categorized
            
            return result
            
        except Exception as e:
            logger.error(f"키워드 추출 중 오류 발생: {str(e)}")
            return {
                "keywords": [],
                "categories": {},
                "top_keywords": [],
                "error": str(e)
            }
    
    async def extract_keywords_batch(
        self, 
        texts: List[str],
        top_n: int = 20,
        classify: bool = True
    ) -> List[Dict[str, Any]]:
        """
        여러 텍스트에서 배치로 키워드 추출
        
        Args:
            texts: 키워드를 추출할 텍스트 목록
            top_n: 추출할 상위 키워드 수
            classify: 카테고리별 분류 여부
            
        Returns:
            List[Dict[str, Any]]: 각 텍스트의 키워드 추출 결과
        """
        if not texts:
            return []
        
        # 병렬 처리
        tasks = [self.extract_keywords(text, top_n, classify) for text in texts]
        results = await asyncio.gather(*tasks)
        
        return results
    
    async def classify_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """
        키워드를 사전 정의된 카테고리로 분류
        
        Args:
            keywords: 분류할 키워드 목록
            
        Returns:
            Dict[str, List[str]]: 카테고리별 키워드 목록
        """
        if not keywords:
            return {cat: [] for cat in self.categories}
        
        # 결과 저장용 딕셔너리
        categorized = {cat: [] for cat in self.categories}
        
        # 직접 단어 매칭을 통한 분류
        remaining_keywords = set(keywords)
        
        # 1. 직접 단어 매칭 (정확한 매칭)
        for keyword in keywords:
            # 이미 분류된 키워드는 건너뜀
            if keyword not in remaining_keywords:
                continue
                
            for category, data in self.categories.items():
                if category == "other":
                    continue
                    
                # 카테고리 키워드 목록
                category_keywords = data["keywords"]
                
                # 직접 포함 관계 확인
                if any(ck in keyword for ck in category_keywords):
                    categorized[category].append(keyword)
                    remaining_keywords.discard(keyword)
                    break
        
        # 2. 벡터 유사도 기반 분류 (남은 키워드에 대해)
        if remaining_keywords and self.category_vectors:
            for keyword in remaining_keywords:
                best_category = "other"
                best_similarity = 0.2  # 최소 유사도 임계값
                
                # 각 카테고리별 유사도 계산
                for category, vectors in self.category_vectors.items():
                    try:
                        vectorizer = vectors["vectorizer"]
                        category_vectors = vectors["vectors"]
                        
                        # 키워드 벡터화
                        keyword_vector = vectorizer.transform([keyword])
                        
                        # 카테고리 키워드들과의 유사도 계산
                        similarities = cosine_similarity(keyword_vector, category_vectors)
                        max_similarity = np.max(similarities)
                        
                        # 최고 유사도 카테고리 선택
                        if max_similarity > best_similarity:
                            best_similarity = max_similarity
                            best_category = category
                            
                    except Exception as e:
                        logger.error(f"유사도 계산 중 오류: {str(e)}")
                
                # 가장 유사한 카테고리에 할당
                categorized[best_category].append(keyword)
        
        # 3. 남은 키워드는 기타 카테고리로 분류
        for keyword in remaining_keywords:
            if not any(keyword in cat_kws for cat, cat_kws in categorized.items() if cat != "other"):
                categorized["other"].append(keyword)
        
        return categorized
    
    async def extract_top_category_keywords(
        self, 
        text: str,
        top_categories: int = 3,
        top_keywords_per_category: int = 5
    ) -> Dict[str, Any]:
        """
        텍스트에서 카테고리별 상위 키워드를 추출
        
        Args:
            text: 분석할 텍스트
            top_categories: 상위 몇 개의 카테고리를 반환할지
            top_keywords_per_category: 카테고리별 상위 몇 개의 키워드를 반환할지
            
        Returns:
            Dict[str, Any]: 카테고리별 상위 키워드
        """
        # 키워드 추출
        extraction_result = await self.extract_keywords(text, top_n=50, classify=True)
        
        categories = extraction_result.get("categories", {})
        
        # 각 카테고리별 키워드 수 계산
        category_counts = {
            cat: len(kws) for cat, kws in categories.items()
        }
        
        # 키워드가 많은 순으로 카테고리 정렬
        sorted_categories = sorted(
            category_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # 상위 N개 카테고리 선택
        top_cats = [cat for cat, count in sorted_categories[:top_categories] if count > 0]
        
        # 결과 형식화
        result = {
            "top_categories": [],
            "all_keywords": extraction_result.get("top_keywords", [])
        }
        
        for cat in top_cats:
            cat_keywords = categories.get(cat, [])[:top_keywords_per_category]
            
            if cat_keywords:
                result["top_categories"].append({
                    "category": cat,
                    "name": self.categories[cat]["name"],
                    "keywords": cat_keywords
                })
        
        return result
    
    async def analyze_sentiment_distribution(
        self, 
        keywords: List[str],
        positive_words: List[str],
        negative_words: List[str]
    ) -> Dict[str, Any]:
        """
        키워드의 긍정/부정 분포 분석
        
        Args:
            keywords: 분석할 키워드 목록
            positive_words: 긍정 단어 목록
            negative_words: 부정 단어 목록
            
        Returns:
            Dict[str, Any]: 감성 분포 분석 결과
        """
        if not keywords:
            return {
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "total": 0,
                "distribution": {
                    "positive": 0.0,
                    "negative": 0.0,
                    "neutral": 0.0
                }
            }
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for keyword in keywords:
            # 긍정 단어와 매칭
            if any(pos in keyword for pos in positive_words):
                positive_count += 1
            # 부정 단어와 매칭
            elif any(neg in keyword for neg in negative_words):
                negative_count += 1
            # 중립으로 분류
            else:
                neutral_count += 1
        
        total = len(keywords)
        
        # 분포 계산
        distribution = {
            "positive": positive_count / total if total > 0 else 0.0,
            "negative": negative_count / total if total > 0 else 0.0,
            "neutral": neutral_count / total if total > 0 else 0.0
        }
        
        return {
            "positive": positive_count,
            "negative": negative_count,
            "neutral": neutral_count,
            "total": total,
            "distribution": distribution
        }


# 싱글톤 인스턴스
_keyword_extractor = None

async def get_extractor() -> KeywordExtractor:
    """
    키워드 추출기의 싱글톤 인스턴스를 반환
    
    Returns:
        KeywordExtractor: 키워드 추출기 인스턴스
    """
    global _keyword_extractor
    
    if _keyword_extractor is None:
        _keyword_extractor = KeywordExtractor()
    
    return _keyword_extractor 