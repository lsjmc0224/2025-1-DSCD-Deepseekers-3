import re
import emoji
import logging
import numpy as np
import tensorflow as tf
from typing import List, Optional, Dict, Union
from soynlp.normalizer import repeat_normalize
from transformers import ElectraTokenizer, TFElectraForSequenceClassification
from kss import split_sentences as kss_split_sentences

# ✅ 로깅 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Analyzer:
    def __init__(self, model_dir: str = "./asset/kcelectra-base-DC", max_length: int = 64):
        self.model_dir = model_dir
        self.max_length = max_length

        try:
            self.tokenizer = ElectraTokenizer.from_pretrained(model_dir)
            self.model = TFElectraForSequenceClassification.from_pretrained(model_dir, num_labels=2)
            self.patterns = self._load_keyword_patterns()
            logger.info("[INIT] 모델 및 키워드 패턴 로딩 완료")
        except Exception as e:
            logger.exception(f"[INIT ERROR] 모델 로딩 실패: {e}")
            raise

    def clean_text(self, content: str, min_length: int = 3, num_repeats: int = 2) -> Optional[str]:
        try:
            _emoji_pattern = emoji.get_emoji_regexp()
            _clean_pattern = re.compile(rf"[^ .,?!/@\$%~％·∼()\x00-\x7Fㄱ-ㅣ가-힣{_emoji_pattern}]+")

            if any(kw in content for kw in ("레시피", "만들기")):
                return None
            if re.search(r"https?://\S+", content):
                return None
            if not re.search(r"[가-힣]", content):
                return None

            cleaned = _clean_pattern.sub(" ", content)
            cleaned = _emoji_pattern.sub("", cleaned)
            cleaned = cleaned.strip()
            cleaned = repeat_normalize(cleaned, num_repeats=num_repeats)

            return cleaned if len(cleaned) >= min_length else None
        except Exception as e:
            logger.warning(f"[CLEAN ERROR] 텍스트 정제 실패: {e}")
            return None

    def split_sentences(self, content: str) -> List[str]:
        try:
            if not isinstance(content, str) or not content.strip():
                return []
            return [s.strip() for s in kss_split_sentences(content) if s.strip()]
        except Exception as e:
            logger.warning(f"[SPLIT ERROR] 문장 분리 실패: {e}")
            return []

    def classify_sentiment(self, content: str) -> int:
        try:
            if not content.strip():
                return -1
            enc = self.tokenizer(
                content,
                return_tensors="tf",
                truncation=True,
                padding="max_length",
                max_length=self.max_length
            )
            outputs = self.model(enc)
            logits = outputs.logits
            probs = tf.nn.softmax(logits, axis=1).numpy()
            return int(np.argmax(probs, axis=1)[0])
        except Exception as e:
            logger.warning(f"[SENTIMENT ERROR] 감성 분류 실패: {e}")
            return -1

    def _load_keyword_patterns(self) -> Dict[str, re.Pattern]:
        keyword_dict = {
            '맛': ['맛있', '달달', '단맛', '짠맛', '맛임', '감칠맛', '매워', '짠', '설탕',
                  '단짠', '밍밍', '매콤', '상큼', '비릿', '인공적', '당충전', '느끼'],
            '식감': ['식감', '쫀득', '쫀득함', '바삭', '퍽퍽', '부드러움', '쫀쫀함', '촉촉',
                   '질겨', '씹싸름', '빠삭', '겉바속촉', '꾸덕', '미끌', '속쫀', '뻑뻑', '사르르'],
            '기타': ['포장', '디자인', '스타일', '편의점', '사진', '인스타', '브랜드', '컬러',
                   '비주', '비주얼', '선물', '리뉴얼', 'CU', 'GS', '세븐', '세븐일레븐',
                   '지에스', '씨유', '이마트', '노브랜드', '이마트24', '배민', 'B마트',
                   '비마트', '팝업', '미니스톱'],
            '가격': ['가격', '가성', '할인', '가성비', '부담', '대비', '싸구려', '가격에비해',
                   '비싸여', '넘비싸', '이딴게', '가심비', '이가격', '합리적'],
            '주관적평가': ['감동', '행복', '만족', '대박', '최고', '실망', '아쉽', '아쉬운', '추천',
                         '진심', '감탄', '존맛', '비추', '느낌', '퀄리티', '재구매', '강추',
                         '굿굿', '중독성', '개존맛']
        }
        return {label: re.compile('|'.join(map(re.escape, keywords)), re.IGNORECASE)
                for label, keywords in keyword_dict.items()}

    def extract_keywords(self, sentence: str) -> List[str]:
        return [label for label, pattern in self.patterns.items() if pattern.search(sentence)]

    def run(self, raw_text: str) -> Dict[str, List[Dict[str, Union[str, int, List[str]]]]]:
        """
        전체 분석 실행 함수
        - 반환 형식: {"contents": [{content, sentiment, keyword_labels}, ...]}
        """
        result: List[Dict[str, Union[str, int, List[str]]]] = []

        logger.info("[RUN] 분석 시작")

        # Step 1: 클리닝
        cleaned = self.clean_text(raw_text)
        if not cleaned:
            logger.warning("[SKIP] 유효하지 않은 텍스트")
            return {"contents": []}

        # Step 2: 문장 분리
        sentences = self.split_sentences(cleaned)
        if not sentences:
            logger.warning("[SKIP] 문장 분리 실패")
            return {"contents": []}

        # Step 3~4: 각 문장에 대해 감성 + 키워드 분석
        for sentence in sentences:
            sentiment = self.classify_sentiment(sentence)
            keywords = self.extract_keywords(sentence)

            if keywords:
                result.append({
                    "content": sentence,
                    "sentiment": sentiment,  # 0: 부정, 1: 긍정
                    "keyword_labels": keywords
                })

        logger.info(f"[DONE] 분석 완료: {len(result)}개 문장")
        return {"contents": result}