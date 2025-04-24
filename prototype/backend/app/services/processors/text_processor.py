"""
텍스트 전처리 및 키워드 추출 모듈

텍스트 정규화, 불용어 제거, 형태소 분석 등 
텍스트 전처리 작업과 키워드 추출 기능을 제공합니다.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import os
from collections import Counter

from konlpy.tag import Okt

# 새로 만든 키워드 추출기 임포트
from app.services.analyzers.keyword_extractor import get_extractor

try:
    import yake
    YAKE_AVAILABLE = True
except ImportError:
    YAKE_AVAILABLE = False

logger = logging.getLogger(__name__)

# KoNLPy 형태소 분석기 초기화
okt = Okt()

# 불용어 리스트 (예시)
STOPWORDS = [
    "들", "은", "는", "이", "가", "의", "에", "에서", "도", "를", "으로", "자", "에게", "인", "듯", "함", "같이", "것", "와", "과",
    "을", "를", "이다", "있다", "하다", "이", "그", "저", "또", "및", "그리고", "그런데", "그래서", "그러나", "그럼", "그렇다",
    "이렇게", "정말", "매우", "너무", "아주", "진짜", "완전", "정말로", "너무너무", "어떤", "이런", "그런", "저런", "어느",
    "http", "https", "www", "com", "co", "kr"
]

# 편의점 디저트 관련 특수 용어 사전
DESSERT_TERMS = {
    "디저트": "디저트",
    "과자": "과자",
    "스낵": "과자",
    "초콜릿": "초콜릿",
    "초콜렛": "초콜릿",
    "초코": "초콜릿",
    "아이스크림": "아이스크림",
    "아이스": "아이스크림",
    "쿠키": "쿠키",
    "파이": "파이",
    "젤리": "젤리",
    "캔디": "캔디",
    "사탕": "캔디",
    "빵": "빵",
    "베이커리": "빵",
    "케이크": "케이크",
    "마카롱": "마카롱",
}


async def preprocess_text(text: str) -> str:
    """
    텍스트를 전처리합니다.
    
    1. HTML 태그 제거
    2. 특수문자 제거
    3. 이모티콘 제거
    4. 불용어 제거
    5. 토큰화 및 형태소 분석
    
    Args:
        text: 전처리할 텍스트
        
    Returns:
        str: 전처리된 텍스트
    """
    # 텍스트가 없는 경우 빈 문자열 반환
    if not text:
        return ""
    
    try:
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # URL 제거
        text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
        
        # 특수문자 제거 (한글, 영문, 숫자, 일부 특수문자만 유지)
        text = re.sub(r'[^\w\s가-힣ㄱ-ㅎㅏ-ㅣ.,!?~-]', ' ', text)
        
        # 이모티콘 제거
        text = re.sub(r'[:;][)(]+', ' ', text)
        
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 형태소 분석 및 불용어 제거
        pos_tagged = okt.pos(text, norm=True, stem=True)
        filtered_words = []
        
        for word, pos in pos_tagged:
            # 명사, 동사, 형용사, 부사만 선택
            if (pos in ['Noun', 'Verb', 'Adjective', 'Adverb'] and 
                len(word) > 1 and word not in STOPWORDS):
                
                # 편의점 디저트 관련 특수 용어 처리
                if word.lower() in DESSERT_TERMS:
                    word = DESSERT_TERMS[word.lower()]
                    
                filtered_words.append(word)
        
        # 전처리된 텍스트 생성
        processed_text = ' '.join(filtered_words)
        
        return processed_text
    
    except Exception as e:
        logger.error(f"텍스트 전처리 중 오류 발생: {str(e)}")
        return text  # 오류 발생 시 원본 텍스트 반환


async def extract_keywords(text: str, top_n: int = 20) -> List[Dict[str, Any]]:
    """
    텍스트에서 주요 키워드를 추출합니다.
    YAKE! 알고리즘을 사용하여 비지도 학습 방식으로 키워드를 추출합니다.
    
    Args:
        text: 키워드를 추출할 텍스트
        top_n: 추출할 최대 키워드 수
        
    Returns:
        List[Dict[str, Any]]: 키워드 및 관련 정보 목록
    """
    # 텍스트가 너무 짧으면 키워드 추출 불가
    if not text or len(text) < 20:
        return []
    
    try:
        # 새로 구현한 키워드 추출기 인스턴스 가져오기
        extractor = await get_extractor()
        
        # 키워드 추출
        result = await extractor.extract_keywords(text, top_n=top_n, classify=True)
        
        # 결과 형식화
        keywords = []
        keyword_items = result.get("keywords", [])
        categories = result.get("categories", {})
        
        # 키워드 정보 구성
        for item in keyword_items:
            keyword = item.get("keyword")
            score = item.get("score", 0.0)
            
            # 카테고리 찾기
            category = "기타"
            for cat_name, cat_keywords in categories.items():
                if keyword in cat_keywords:
                    if cat_name == "taste":
                        category = "맛"
                    elif cat_name == "price":
                        category = "가격"
                    elif cat_name == "packaging":
                        category = "패키징"
                    elif cat_name == "place":
                        category = "판매처"
                    elif cat_name == "repurchase":
                        category = "재구매"
                    break
            
            keywords.append({
                "keyword": keyword,
                "score": score,
                "category": category,
                "extraction_date": datetime.now().isoformat()
            })
        
        return keywords
        
    except Exception as e:
        logger.error(f"키워드 추출 중 오류 발생: {str(e)}")
        
        # 오류 발생 시 기존 방식으로 키워드 추출 시도
        try:
            # YAKE 키워드 추출기 설정
            kw_extractor = yake.KeywordExtractor(
                lan="ko",             # 한국어
                n=2,                  # 최대 2-gram
                dedupLim=0.9,         # 중복 제거 임계값
                dedupFunc="seqm",     # 중복 제거 함수
                windowsSize=3,        # 윈도우 크기
                top=top_n,            # 상위 키워드 수
                features=None
            )
            
            # 키워드 추출
            raw_keywords = kw_extractor.extract_keywords(text)
            
            # 결과 형식화
            keywords = []
            for kw, score in raw_keywords:
                # 점수가 낮을수록 중요도 높음 (YAKE 알고리즘 특성)
                # 1.0에서 빼서 0~1 사이 점수로 변환 (높을수록 중요)
                importance = max(0, min(1, 1.0 - score))
                
                # 기본 카테고리 설정
                category = "기타"
                
                # 키워드 카테고리 분류
                if any(term in kw.lower() for term in ["맛", "달다", "짜다", "시다", "쓰다", "향", "식감"]):
                    category = "맛"
                elif any(term in kw.lower() for term in ["가격", "비싸다", "저렴", "원", "만원", "천원", "비용"]):
                    category = "가격"
                elif any(term in kw.lower() for term in ["포장", "박스", "상자", "패키지", "용기", "디자인"]):
                    category = "패키징"
                elif any(term in kw.lower() for term in ["씨유", "cu", "gs", "지에스", "세븐", "미니스톱", "이마트", "gs25", "cu", "7eleven"]):
                    category = "판매처"
                elif any(term in kw.lower() for term in ["다시", "또", "재구매", "추천", "사먹", "살", "살것"]):
                    category = "재구매"
                
                keywords.append({
                    "keyword": kw,
                    "score": importance,
                    "category": category,
                    "extraction_date": datetime.now().isoformat()
                })
            
            return keywords
            
        except Exception as nested_e:
            logger.error(f"대체 키워드 추출 방식에서도 오류 발생: {str(nested_e)}")
            return []


async def categorize_keywords(keywords: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    추출된 키워드를 카테고리별로 분류합니다.
    
    Args:
        keywords: 추출된 키워드 목록
        
    Returns:
        Dict[str, List[Dict[str, Any]]]: 카테고리별로 분류된 키워드
    """
    categories = {
        "맛": [],      # 맛 관련
        "가격": [],    # 가격 관련
        "패키징": [],  # 패키징 관련
        "판매처": [],  # 판매처 관련
        "재구매": [],  # 재구매 의향 관련
        "기타": []     # 기타
    }
    
    for keyword in keywords:
        category = keyword.get("category", "기타")
        if category in categories:
            categories[category].append(keyword)
        else:
            categories["기타"].append(keyword)
    
    return categories


async def extract_categorized_keywords(text: str, top_n: int = 20) -> Dict[str, Any]:
    """
    텍스트에서 키워드를 추출하고 바로 카테고리별로 분류합니다.
    
    Args:
        text: 키워드를 추출할 텍스트
        top_n: 추출할 최대 키워드 수
        
    Returns:
        Dict[str, Any]: 카테고리별 키워드와 메타 정보
    """
    try:
        # 전처리 수행
        preprocessed_text = await preprocess_text(text)
        
        # 새로 구현한 키워드 추출기 사용
        extractor = await get_extractor()
        
        # 카테고리별 상위 키워드 추출
        result = await extractor.extract_top_category_keywords(
            preprocessed_text,
            top_categories=5,
            top_keywords_per_category=5
        )
        
        # 메타 정보 추가
        result["analysis_timestamp"] = datetime.now().isoformat()
        result["text_length"] = len(text)
        result["preprocessed_length"] = len(preprocessed_text)
        
        return result
        
    except Exception as e:
        logger.error(f"카테고리별 키워드 추출 중 오류 발생: {str(e)}")
        
        # 오류 발생 시 기존 방식으로 대체
        try:
            keywords = await extract_keywords(text, top_n)
            categorized = await categorize_keywords(keywords)
            
            # 결과 형식화
            result = {
                "top_categories": [],
                "all_keywords": [kw["keyword"] for kw in keywords],
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            # 카테고리별 키워드 정보 구성
            for cat_name, cat_keywords in categorized.items():
                if cat_keywords:
                    result["top_categories"].append({
                        "category": cat_name,
                        "name": cat_name,  # 한글 카테고리명 사용
                        "keywords": [kw["keyword"] for kw in cat_keywords[:5]]
                    })
            
            return result
            
        except Exception as nested_e:
            logger.error(f"대체 카테고리 분류 방식에서도 오류 발생: {str(nested_e)}")
            return {
                "top_categories": [],
                "all_keywords": [],
                "analysis_timestamp": datetime.now().isoformat(),
                "error": str(e)
            }


class TextProcessor:
    """
    텍스트 처리를 위한 클래스.
    텍스트 정규화, 키워드 추출 등의 기능을 제공합니다.
    """
    
    def __init__(self, stopwords_file: Optional[str] = None):
        """
        텍스트 처리기를 초기화합니다.
        
        Args:
            stopwords_file: 불용어 목록 파일 경로
        """
        # 기본 불용어 목록
        self.stopwords = set([
            "이", "그", "저", "것", "이것", "그것", "저것", "이거", "그거", "저거", 
            "이런", "그런", "저런", "어떤", "무슨", "어느", "아", "휴", "아이구", "아이쿠", 
            "아이고", "어", "나", "우리", "저희", "당신", "너", "너희", "여러분", "그녀", 
            "그들", "저들", "제가", "부터", "그부터", "하지만", "그러나", "그렇지만", "그리고", 
            "한다", "합니다", "하다", "하였다", "했다", "하는", "하면", "하고", "한", "할", "하자",
            "거", "더", "또", "매우", "정말", "진짜", "약간", "조금", "이렇게", "그렇게", "저렇게",
            "라며", "이라며", "음", "은", "는", "이런", "저런", "하며", "이라", "이라고", "하서", 
            "을", "를", "에", "의", "가", "이", "와", "과", "도", "에서", "으로", "로", "에게",
            "뿐", "다", "의", "거의", "겨우", "고작", "다만", "불과", "시작하다", "시작했다"
        ])
        
        # 불용어 목록 파일이 제공된 경우 로드
        if stopwords_file and os.path.exists(stopwords_file):
            self._load_stopwords(stopwords_file)
        
        # 상품 카테고리 목록
        self.product_categories = {
            "음료": ["커피", "차", "주스", "음료수", "물", "탄산", "우유", "음료", "두유", "에이드"],
            "과자": ["과자", "스낵", "칩", "쿠키", "초콜릿", "사탕", "젤리", "초코", "캔디"],
            "빵/디저트": ["빵", "케이크", "베이커리", "도넛", "페이스트리", "디저트", "샌드위치", "파이", "타르트"],
            "아이스크림": ["아이스크림", "아이스바", "콘", "아이스", "설빙", "빙수", "아이스티"],
            "편의식품": ["김밥", "도시락", "샐러드", "삼각김밥", "샌드위치", "햄버거", "핫도그", "라면"],
            "즉석식품": ["즉석밥", "즉석국", "레토르트", "냉동식품", "즉석식품", "컵밥", "컵반", "컵라면"],
            "유제품": ["우유", "요거트", "치즈", "버터", "유제품"],
            "주류": ["맥주", "소주", "와인", "막걸리", "주류", "위스키", "보드카", "칵테일"],
            "건강식품": ["에너지바", "프로틴", "보충제", "건강보조식품", "비타민"],
            "일반": ["편의점", "신상", "신제품", "행사", "할인", "이벤트", "추천", "리뷰"]
        }
    
    def _load_stopwords(self, file_path: str):
        """
        파일에서 불용어 목록을 로드합니다.
        
        Args:
            file_path: 불용어 목록 파일 경로
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    # JSON 형식인 경우
                    stopwords = set(json.load(f))
                else:
                    # 텍스트 파일인 경우 (한 줄에 한 단어)
                    stopwords = set(line.strip() for line in f if line.strip())
                    
                self.stopwords = stopwords
                    
        except Exception as e:
            print(f"불용어 목록 파일 로드 오류: {e}")
    
    def normalize_text(self, text: str) -> str:
        """
        텍스트를 정규화합니다.
        
        Args:
            text: 정규화할 텍스트
            
        Returns:
            정규화된 텍스트
        """
        if not text:
            return ""
        
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # URL 제거
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # 이메일 주소 제거
        text = re.sub(r'\S+@\S+', '', text)
        
        # 특수 문자 및 숫자 제거 (한글, 영문, 공백만 남김)
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        
        # 숫자 제거
        text = re.sub(r'\d+', '', text)
        
        # 연속된 공백을 하나의 공백으로 변환
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_keywords_yake(self, text: str, max_keywords: int = 10, 
                            language: str = "ko") -> List[Tuple[str, float]]:
        """
        YAKE를 사용하여 텍스트에서 키워드를 추출합니다.
        
        Args:
            text: 키워드를 추출할 텍스트
            max_keywords: 추출할 최대 키워드 수
            language: 텍스트 언어
            
        Returns:
            (키워드, 점수) 튜플 목록
        """
        if not YAKE_AVAILABLE:
            print("YAKE 라이브러리가의 설치되지 않았습니다.")
            return []
        
        if not text:
            return []
        
        try:
            # YAKE 설정
            kw_extractor = yake.KeywordExtractor(
                lan=language,
                n=1,  # 1-gram
                dedupLim=0.9,  # 중복 제거 임계값
                dedupFunc='seqm',  # 중복 제거 함수
                windowsSize=1,  # 윈도우 크기
                top=max_keywords,  # 최대 키워드 수
                features=None
            )
            
            # 키워드 추출
            keywords = kw_extractor.extract_keywords(text)
            
            # YAKE에서는 점수가 낮을수록 더 중요한 키워드이므로 내림차순으로 정렬
            keywords.sort(key=lambda x: x[1])
            
            # 불용어 제거
            filtered_keywords = [(kw, score) for kw, score in keywords 
                               if kw.lower() not in self.stopwords and len(kw) > 1]
            
            return filtered_keywords[:max_keywords]
            
        except Exception as e:
            print(f"YAKE 키워드 추출 오류: {e}")
            return []
    
    def extract_keywords_simple(self, text: str, max_keywords: int = 10) -> List[Tuple[str, int]]:
        """
        간단한 빈도 기반 키워드 추출 방법.
        YAKE를 사용할 수 없을 때 대체 방법으로 사용합니다.
        
        Args:
            text: 키워드를 추출할 텍스트
            max_keywords: 추출할 최대 키워드 수
            
        Returns:
            (키워드, 빈도) 튜플 목록
        """
        if not text:
            return []
        
        # 텍스트 정규화
        normalized_text = self.normalize_text(text)
        
        # 단어 분리
        words = normalized_text.split()
        
        # 불용어 제거 및 길이가 1인 단어 제거
        filtered_words = [word for word in words 
                         if word.lower() not in self.stopwords and len(word) > 1]
        
        # 단어 빈도 계산
        word_counts = Counter(filtered_words)
        
        # 가장 빈도가 높은 단어 추출
        return word_counts.most_common(max_keywords)
    
    def extract_keywords(self, text: str, max_keywords: int = 10, 
                       use_yake: bool = True) -> List[Tuple[str, float]]:
        """
        텍스트에서 키워드를 추출합니다.
        
        Args:
            text: 키워드를 추출할 텍스트
            max_keywords: 추출할 최대 키워드 수
            use_yake: YAKE 알고리즘 사용 여부
            
        Returns:
            (키워드, 점수) 튜플 목록
        """
        if use_yake and YAKE_AVAILABLE:
            return self.extract_keywords_yake(text, max_keywords)
        else:
            return self.extract_keywords_simple(text, max_keywords)
    
    def categorize_keywords(self, keywords: List[Tuple[str, Any]]) -> Dict[str, List[Tuple[str, Any]]]:
        """
        추출된 키워드를 카테고리별로 분류합니다.
        
        Args:
            keywords: (키워드, 점수) 튜플 목록
            
        Returns:
            카테고리별 키워드 목록
        """
        categorized = {category: [] for category in self.product_categories}
        categorized["기타"] = []  # 분류되지 않은 키워드를 위한 카테고리
        
        for keyword, score in keywords:
            keyword_lower = keyword.lower()
            
            # 키워드가 속한 카테고리 찾기
            categorized_flag = False
            for category, terms in self.product_categories.items():
                if any(term in keyword_lower for term in terms):
                    categorized[category].append((keyword, score))
                    categorized_flag = True
                    break
            
            # 분류되지 않은 경우 '기타' 카테고리에 추가
            if not categorized_flag:
                categorized["기타"].append((keyword, score))
        
        # 빈 카테고리 제거
        return {k: v for k, v in categorized.items() if v}
    
    def analyze_text(self, text: str, max_keywords: int = 20) -> Dict[str, Any]:
        """
        텍스트를 분석하여 정규화, 키워드 추출, 키워드 분류 결과를 반환합니다.
        
        Args:
            text: 분석할 텍스트
            max_keywords: 추출할 최대 키워드 수
            
        Returns:
            분석 결과
        """
        if not text:
            return {
                "original_length": 0,
                "normalized_length": 0,
                "keywords": [],
                "categorized_keywords": {}
            }
        
        # 텍스트 정규화
        normalized_text = self.normalize_text(text)
        
        # 키워드 추출
        keywords = self.extract_keywords(normalized_text, max_keywords)
        
        # 키워드 분류
        categorized_keywords = self.categorize_keywords(keywords)
        
        return {
            "original_length": len(text),
            "normalized_length": len(normalized_text),
            "keywords": keywords,
            "categorized_keywords": categorized_keywords
        }
    
    def analyze_comments(self, comments: List[Dict[str, Any]], 
                        text_key: str = "text", max_keywords: int = 30) -> Dict[str, Any]:
        """
        댓글 목록을 분석하여 종합적인 분석 결과를 반환합니다.
        
        Args:
            comments: 댓글 목록 (각 댓글은 딕셔너리 형태)
            text_key: 댓글 텍스트가 저장된 키 이름
            max_keywords: 추출할 최대 키워드 수
            
        Returns:
            분석 결과
        """
        if not comments:
            return {
                "comment_count": 0,
                "total_text_length": 0,
                "keywords": [],
                "categorized_keywords": {}
            }
        
        # 모든 댓글 텍스트를 하나로 합치기
        all_comments_text = " ".join(comment.get(text_key, "") for comment in comments if text_key in comment)
        
        # 텍스트 분석
        analysis_result = self.analyze_text(all_comments_text, max_keywords)
        
        # 결과 구성
        return {
            "comment_count": len(comments),
            "total_text_length": analysis_result["original_length"],
            "keywords": analysis_result["keywords"],
            "categorized_keywords": analysis_result["categorized_keywords"]
        }
    
    def analyze_transcript(self, transcript_data: Dict[str, Any], 
                         max_keywords: int = 30) -> Dict[str, Any]:
        """
        자막 데이터를 분석합니다.
        
        Args:
            transcript_data: 자막 데이터 (full_text, sentences 포함)
            max_keywords: 추출할 최대 키워드 수
            
        Returns:
            분석 결과
        """
        if not transcript_data or "full_text" not in transcript_data:
            return {
                "transcript_length": 0,
                "sentence_count": 0,
                "keywords": [],
                "categorized_keywords": {}
            }
        
        full_text = transcript_data.get("full_text", "")
        sentences = transcript_data.get("sentences", [])
        
        # 텍스트 분석
        analysis_result = self.analyze_text(full_text, max_keywords)
        
        return {
            "transcript_length": analysis_result["original_length"],
            "sentence_count": len(sentences),
            "keywords": analysis_result["keywords"],
            "categorized_keywords": analysis_result["categorized_keywords"]
        } 