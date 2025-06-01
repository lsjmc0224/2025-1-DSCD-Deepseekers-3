"""
sentiment.py

모듈화된 감성 분류기

함수:
  - load_sentiment_model: 저장된 KcELECTRA 모델/토크나이저 로드
  - predict_sentiment_df: 분리된 문장 DataFrame에 감성 추론 후 라벨 및 확률 컬럼 추가

CLI:
  --input       : 입력 CSV 경로 (ID, 작성시간, cleaned, divided_comment 포함)
  --output      : 출력 CSV 경로
  --model-dir   : HuggingFace 포맷 모델 디렉토리 (config.json, tf_model.h5, vocab 등)
  --text-col    : 분류할 텍스트 컬럼 (기본: 'divided_comment')
  --output-col  : 예측 라벨 컬럼명 (기본: 'sentiment')
  --max-length  : 토큰 최대 길이 (기본: 64)
  --batch-size  : 배치 크기 (기본: 16)
  --preview     : True일 때 샘플 10개 확인
"""

import os
import time
import argparse
import pandas as pd
import numpy as np
import tensorflow as tf
from transformers import ElectraTokenizer, TFElectraForSequenceClassification
from ace_tools_open import display_dataframe_to_user


def load_sentiment_model(model_dir: str):
    """
    저장된 KcELECTRA 모델/토크나이저 로드
    model_dir 내부에 config.json, tf_model.h5, vocab.txt, tokenizer_config.json,
    special_tokens_map.json 등이 있어야 함
    """
    tokenizer = ElectraTokenizer.from_pretrained(model_dir)
    model = TFElectraForSequenceClassification.from_pretrained(
        model_dir,
        num_labels=2
    )
    return tokenizer, model


def predict_sentiment_df(
    df: pd.DataFrame,
    tokenizer,
    model,
    text_col: str = 'divided_comment',
    output_col: str = 'sentiment',
    max_length: int = 64,
    batch_size: int = 16
) -> pd.DataFrame:
    """
    분리된 문장 DataFrame(df)에 대해 감성 분류 수행
    - output_col: 예측 라벨 컬럼명
    - output_col_prob_0, output_col_prob_1: softmax 확률 컬럼 추가
    """
    texts = df[text_col].fillna('').astype(str).tolist()
    enc = tokenizer(
        texts,
        return_tensors='tf',
        padding='max_length',
        truncation=True,
        max_length=max_length
    )
    ds = tf.data.Dataset.from_tensor_slices(dict(enc)).batch(batch_size)

    start = time.perf_counter()
    preds = model.predict(ds)
    elapsed = time.perf_counter() - start

    probs = tf.nn.softmax(preds.logits, axis=1).numpy()
    labels = np.argmax(probs, axis=1)

    df[output_col] = labels
    df[f'{output_col}_prob_0'] = probs[:, 0]
    df[f'{output_col}_prob_1'] = probs[:, 1]

    print(f"[SENTI] {len(texts)} samples → {elapsed:.2f}s total, {elapsed/len(texts):.4f}s per sample")
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='감성 분류 모듈')
    parser.add_argument('--input',      '-i', required=True, help='입력 CSV 파일 경로')
    parser.add_argument('--output',     '-o', required=True, help='출력 CSV 파일 경로')
    parser.add_argument('--model-dir',  '-m', required=True, help='모델 디렉토리 경로')
    parser.add_argument('--text-col',   default='divided_comment', help='분류할 텍스트 컬럼')
    parser.add_argument('--output-col', default='sentiment',         help='예측 라벨 컬럼명')
    parser.add_argument('--max-length', type=int, default=64,         help='토큰 최대 길이')
    parser.add_argument('--batch-size', type=int, default=16,         help='배치 크기')
    parser.add_argument('--preview',    action='store_true',         help='샘플 확인')
    args = parser.parse_args()

    df = pd.read_csv(args.input, encoding='utf-8-sig')
    tokenizer, model = load_sentiment_model(args.model_dir)
    df_out = predict_sentiment_df(
        df,
        tokenizer,
        model,
        text_col=args.text_col,
        output_col=args.output_col,
        max_length=args.max_length,
        batch_size=args.batch_size
    )

    if args.preview:
        display_dataframe_to_user('감성 분류 예시', df_out.head(10))

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df_out.to_csv(args.output, index=False, encoding='utf-8-sig')
    print(f"[SENTI] 저장 완료: {args.output}")
