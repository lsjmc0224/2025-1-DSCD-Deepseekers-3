# infer.py

import os
import time
import re
import numpy as np
import pandas as pd
import tensorflow as tf
import emoji
from soynlp.normalizer import repeat_normalize
from transformers import BertTokenizer
from sklearn.metrics import classification_report, confusion_matrix

# 실제 모듈 이름에 맞춰 경로 수정
from Fine_tuning import CustomTFElectraForSequenceClassification, to_categorical

# ── 1) 실행 시에 여기만 바꾸세요 ────────────────────────────────────
MAX_LENGTH     = 64   
# <-- 16 또는 64 or 128
# ─────────────────────────────────────────────────────────────────

# ── 2) 경로 설정 ─────────────────────────────────────────────────
DATA_DIR       = r"C:\Users\parkm\OneDrive - dgu.ac.kr\DC\JICS-NLP-2024\1.Data"
CKPT_ROOT      = r"C:\Users\parkm\OneDrive - dgu.ac.kr\DC\JICS-NLP-2024\checkpoints\64"
TEST_CSV       = os.path.join(DATA_DIR, "test_data_1000.csv")
TOKENIZER_NAME = "beomi/KcELECTRA-base-v2022"
MODEL_NAME     = TOKENIZER_NAME
BATCH_SIZE     = 16

# 체크포인트, 결과 저장 디렉토리 (예: ...\checkpoints\64)
output_dir = os.path.join(CKPT_ROOT, str(MAX_LENGTH))
os.makedirs(output_dir, exist_ok=True)

# ── 3) clean 함수 정의 ────────────────────────────────────────────
emojis       = ''.join(emoji.EMOJI_DATA.keys())
pattern      = re.compile(f'[^ .,?!/@$%~％·∼()\x00-\x7Fㄱ-ㅣ가-힣{emojis}]+')
url_pattern  = re.compile(
    r'https?://(www\.)?[-A-Za-z0-9@:%._\+~#=]{1,256}\.[A-Za-z0-9()]{1,6}\b([-A-Za-z0-9()@:%_\+.~#?&//=]*)'
)
def clean(text: str) -> str:
    text = pattern.sub(' ', text)
    text = emoji.replace_emoji(text, replace='')
    text = url_pattern.sub('', text)
    text = text.strip()
    return repeat_normalize(text, num_repeats=2)

# ── 4) 테스트 데이터 준비 ─────────────────────────────────────────
df = pd.read_csv(TEST_CSV, encoding='utf-8')
df['comment'] = df['comment'].map(clean)

X_test = df['comment'].tolist()
y_true = df['sentiment'].values
y_test  = to_categorical(y_true)

# ── 5) 모델 & 체크포인트 로드 ─────────────────────────────────────
tokenizer = BertTokenizer.from_pretrained(TOKENIZER_NAME)
model     = CustomTFElectraForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=2, from_pt=True
)

ckpt_prefix = os.path.join(
    CKPT_ROOT,
    f"checkpoint_{MODEL_NAME.replace('/', '_')}_maxlen_{MAX_LENGTH}"
)
status = model.load_weights(ckpt_prefix)
status.expect_partial()  # optimizer state 등 경고 무시

# ── 6) Dataset 생성 ───────────────────────────────────────────────
tok = tokenizer(
    X_test,
    return_tensors="tf",
    max_length=MAX_LENGTH,
    padding="max_length",
    truncation=True
)
test_ds = tf.data.Dataset.from_tensor_slices((dict(tok), y_test)) \
                         .batch(BATCH_SIZE)

# ── 7) Inference & 시간 측정 ─────────────────────────────────────
start = time.perf_counter()
pred = model.predict(test_ds)
elapsed = time.perf_counter() - start

probs = tf.nn.softmax(pred.logits, axis=1).numpy()
y_pred = np.argmax(probs, axis=1)

# ── 8) 메트릭 계산 & CSV 저장 ────────────────────────────────────
report = classification_report(y_true, y_pred, output_dict=True)
tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

metrics = {
    "attribute": "sentiment",
    "accuracy": report['accuracy'],
    "precision_macro": report['macro avg']['precision'],
    "recall_macro": report['macro avg']['recall'],
    "f1_macro": report['macro avg']['f1-score'],
    "precision_class_0": report['0']['precision'],
    "recall_class_0": report['0']['recall'],
    "f1_class_0": report['0']['f1-score'],
    "precision_class_1": report['1']['precision'],
    "recall_class_1": report['1']['recall'],
    "f1_class_1": report['1']['f1-score'],
    "confusion_matrix_tn_fp_fn_tp": f"[{tn}, {fp}, {fn}, {tp}]"
}
metrics_df = pd.DataFrame([metrics])

csv_path = os.path.join(output_dir, f"sentiment_metrics_{MAX_LENGTH}.csv")
metrics_df.to_csv(csv_path, index=False, encoding='utf-8-sig')

# ── 9) 결과 출력 ─────────────────────────────────────────────────
print(f"\n=== MAX_LENGTH = {MAX_LENGTH} ===")
print(f"Inference time: {elapsed:.2f}s total, {elapsed/len(X_test):.4f}s per sample\n")
print(metrics_df.to_string(index=False))
print(f"\n[Saved metrics to {csv_path}]\n")

# ── 10) 랜덤 샘플 10개 확인 ───────────────────────────────────────
sample = df[['comment','sentiment']].sample(10, random_state=42)
print("=== Random 10 Samples (cleaned + label) ===")
print(sample.to_string(index=False))
