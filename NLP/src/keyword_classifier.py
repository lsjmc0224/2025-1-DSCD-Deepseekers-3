"""
    keyword_classifier.py

    멀티레이블 키워드 추출 모듈

    함수:
      - load_patterns: 사전 정의된 키워드 리스트를 패턴 딕셔너리로 변환
      - classify_keywords_df: DataFrame에 대해 각 키워드 패턴에 맞춰 0/1 레이블 컬럼 추가

    CLI:
      --input       : 입력 CSV 경로 (ID, divided_comment, sentiment_pred 포함)
      --output      : 출력 CSV 경로
      --text-col    : 텍스트 컬럼명 (기본: 'divided_comment')
      --preview     : True일 때 샘플 20개 표출

    사용 예시:
      python keyword_classifier.py \
        --input data/step3_sentiment.csv \
        --output data/step4_keywords.csv \
        --preview
"""

import argparse
import pandas as pd
import re
from ace_tools_open import display_dataframe_to_user


def load_patterns() -> dict:
    """
    사전 정의된 키워드 리스트를 regex 패턴 dict로 컴파일하여 반환
    """
    keyword_dict = {
        '맛': [
            '맛있','달달','단맛','짠맛','맛임','감칠맛','매워','짠','설탕',
            '단짠','밍밍','매콤','상큼','비릿','인공적','당충전', '느끼'
        ],
        '식감': [
            '식감','쫀득','쫀득함','바삭','퍽퍽','부드러움','쫀쫀함','촉촉',
            '질겨','씹싸름','빠삭','겉바속촉','꾸덕','미끌','속쫀','뻑뻑','사르르'
        ],
        '기타': [
            '포장','디자인','스타일','편의점','사진','인스타','브랜드','컬러',
            '비주','비주얼','선물','리뉴얼','CU','GS','세븐','세븐일레븐',
            '지에스','씨유','이마트','노브랜드','이마트24','배민','B마트',
            '비마트','팝업','미니스톱'
        ],
        '가격': [
            '가격','가성','할인','가성비','부담','대비','싸구려','가격에비해',
            '비싸여','넘비싸','이딴게','가심비','이가격','합리적'
        ],
        '주관적평가': [
            '감동','행복','만족','대박','최고','실망','아쉽','아쉬운','추천',
            '진심','감탄','존맛','비추','느낌','퀄리티','재구매','강추',
            '굿굿','중독성','개존맛'
        ]
    }
    # regex 컴파일
    patterns = {}
    for label, kw_list in keyword_dict.items():
        # OR 결합, ignore case
        regex = re.compile('|'.join(map(re.escape, kw_list)), flags=re.IGNORECASE)
        patterns[label] = regex
    return patterns


def classify_keywords_df(
    df: pd.DataFrame,
    text_col: str = 'divided_comment'
) -> pd.DataFrame:
    """
    1) text_col 기준으로 패턴 매칭해 0/1 컬럼 추가
    2) 아무 키워드에도 매칭되지 않은(모든 컬럼 0) 행은 삭제
    """
    patterns = load_patterns()
    label_cols = list(patterns.keys())

    # 1) 각 패턴별 매칭 여부 컬럼 생성
    for label, pat in patterns.items():
        df[label] = df[text_col].str.contains(pat).astype(int)

    # 2) 모든 키워드 컬럼이 0인 행 DROP
    mask = df[label_cols].sum(axis=1) > 0
    df_filtered = df[mask].reset_index(drop=True)

    return df_filtered


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='키워드 기반 멀티레이블 분류 모듈')
    parser.add_argument('--input',   '-i', required=True, help='입력 CSV 파일 경로')
    parser.add_argument('--output',  '-o', required=True, help='출력 CSV 파일 경로')
    parser.add_argument('--text-col', default='divided_comment', help='텍스트 컬럼명')
    parser.add_argument('--preview', action='store_true', help='샘플 20개 출력')
    args = parser.parse_args()

    df = pd.read_csv(args.input, encoding='utf-8-sig')
    df_out = classify_keywords_df(df, text_col=args.text_col)

    if args.preview:
        cols = ['ID', args.text_col, 'sentiment'] + list(load_patterns().keys())
        display_dataframe_to_user('키워드 분류 예시', df_out[cols].head(20))

    df_out.to_csv(args.output, index=False, encoding='utf-8-sig')
    print(f"[KEYWORD] 저장 완료: {args.output} | 레이블: {', '.join(load_patterns().keys())}")