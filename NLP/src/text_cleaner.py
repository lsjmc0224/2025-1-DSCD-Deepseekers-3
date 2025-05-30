"""
    text_cleaner.py

    모듈화된 텍스트 정제기

    함수:
        - clean_text: 단일 문자열 정제 -> str 또는 None 반환
        - clean_dataframe: DataFrame에 clean_text 적용, 정제된 DataFrame 반환 및 실행 시간/삭제 행 수 출력
"""

import re
import emoji
import time
import pandas as pd
from typing import Optional
from soynlp.normalizer import repeat_normalize

# 허용 문자 패턴
_EMOJI_PATTERN = emoji.get_emoji_regexp()
_CLEAN_PATTERN = re.compile(
    rf"[^ .,?!/@\$%~％·∼()\x00-\x7Fㄱ-ㅣ가-힣{_EMOJI_PATTERN}]+"
)
_URL_PATTERN = re.compile(r"https?://\S+")


def clean_text(
    text: str,
    min_length: int = 3,
    num_repeats: int = 2
) -> Optional[str]:
    """
    텍스트 정제:
    - '레시피', '만들기' 키워드, URL, 한글 없는 댓글 None 반환
    - 허용 문자만 남김
    - 이모지 제거
    - 공백 strip
    - 반복문자 정규화
    - min_length 이하이면 None 반환
    이 모든 필터 통과시 정제된 문자열 반환한다.
    """
    # 삭제 조건
    if any(kw in text for kw in ("레시피", "만들기")):
        return None
    if _URL_PATTERN.search(text):
        return None
    if not re.search(r"[가-힣]", text):
        return None

    # 정제 로직
    cleaned = _CLEAN_PATTERN.sub(" ", text)
    cleaned = _EMOJI_PATTERN.sub("", cleaned)
    cleaned = cleaned.strip()
    cleaned = repeat_normalize(cleaned, num_repeats=num_repeats)
    if len(cleaned) < min_length:
        return None
    return cleaned


def clean_dataframe(
    df: pd.DataFrame,
    text_col: str = "comment",
    min_length: int = 3,
    num_repeats: int = 2
) -> pd.DataFrame:
    """
    DataFrame에 clean_text 적용:
    - original 행 수, 삭제된 행 수, 처리 시간 출력
    - 'cleaned' 컬럼에 정제된 텍스트 저장
    - None인 행은 삭제
    """
    start = time.perf_counter()
    total = len(df)
    df['cleaned'] = df[text_col].apply(
        lambda x: clean_text(x, min_length, num_repeats)
    )
    df_clean = df.dropna(subset=['cleaned']).reset_index(drop=True)
    dropped = total - len(df_clean)
    elapsed = time.perf_counter() - start
    print(f"[CLEAN] 처리 시간: {elapsed:.2f}s | 총 행: {total} | 삭제된 행: {dropped}")
    return df_clean

#CLI 지원
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="텍스트 정제 모듈"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="입력 CSV 파일 경로 (comment 컬럼 포함)"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="출력 CSV 파일 경로"
    )
    parser.add_argument(
        "--min_length", type=int, default=3,
        help="최소 길이 (default=3)"
    )
    parser.add_argument(
        "--num_repeats", type=int, default=2,
        help="반복문자 정규화 허용 횟수 (default=2)"
    )
    args = parser.parse_args()

    df = pd.read_csv(args.input, encoding="utf-8-sig")
    df_clean = clean_dataframe(
        df,
        text_col="comment",
        min_length=args.min_length,
        num_repeats=args.num_repeats
    )
    df_clean.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"정제된 데이터 저장: {args.output}")
