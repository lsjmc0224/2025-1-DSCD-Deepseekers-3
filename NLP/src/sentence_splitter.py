"""
    sentence_splitter.py

    모듈화된 문장 분할기

    함수:
        - split_sentences_df: DataFrame을 받아서 cleaned 컬럼 기준으로 문장 분리 후 explode
        - sample_preview: 샘플 데이터를 로드 후 분할 결과를 display
"""

import argparse
import pandas as pd
from kss import split_sentences
from ace_tools_open import display_dataframe_to_user
from typing import Optional

def split_sentences_df(
    df: pd.DataFrame,
    id_col: str = 'ID',
    time_col: Optional[str] = None, 
    text_col: str = 'cleaned',
    output_col: str = 'divided_comment'
) -> pd.DataFrame:
    """
    DataFrame에서 한 줄(comment/cleaned)마다 문장 분리 후 explode 처리

    Args:
        df: 원본 DataFrame
        id_col: ID 컬럼명
        time_col: 작성시간 컬럼명 (없으면 None)
        text_col: 분할할 텍스트 컬럼명
        output_col: 분할된 문장을 담을 컬럼명

    Returns:
        exploded_df: id, time(선택), original_comment, cleaned, divided_comment이 포함된 DataFrame
    """
    # 문장 리스트 컬럼 생성
    df['sent_list'] = df[text_col].apply(lambda x: split_sentences(x) if isinstance(x, str) else [])
    # explode
    df_exploded = df.explode('sent_list').reset_index(drop=True)
    # 컬럼명 변경
    df_exploded = df_exploded.rename(columns={'sent_list': output_col})
    # 최종 컬럼 순서
    cols = [id_col]
    if time_col and time_col in df_exploded.columns:
        cols.append(time_col)
    cols += [text_col, output_col]
    available = [c for c in cols if c in df_exploded.columns] #df_exploded에 cols중 실제로 있는 컬럼만 골라서 출력
    return df_exploded[available]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='문장 분할 모듈')
    parser.add_argument('-i', '--input', required=True, help='입력 CSV 파일 경로')
    parser.add_argument('-o', '--output', required=True, help='출력 CSV 파일 경로')
    parser.add_argument('--id-col', default='ID', help='ID 컬럼명')
    parser.add_argument('--time-col', default=None, help='작성시간 컬럼명')
    parser.add_argument('--text-col', default='cleaned', help='분할할 텍스트 컬럼명')
    parser.add_argument('--output-col', default='divided_comment', help='분할된 문장 컬럼명')
    parser.add_argument('--preview', action='store_true', help='샘플 20개 미리보기')
    args = parser.parse_args()

    df = pd.read_csv(args.input, encoding='utf-8-sig')
    df_split = split_sentences_df(
        df,
        id_col=args.id_col,
        time_col=args.time_col,
        text_col=args.text_col,
        output_col=args.output_col
    )

    if args.preview:
        display_dataframe_to_user('분리된 문장 예시', df_split.head(20))

    df_split.to_csv(args.output, index=False, encoding='utf-8-sig')
    print(f"[SPLIT] 저장 완료: {args.output} | 총 행: {len(df_split)}")
