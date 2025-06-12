# NLP 파이프라인 프로젝트

## 📁 디렉터리 구조
kcelectra-base-DC/              ← GitHub·Hugging Face 공통 루트

├─requirements
│
├─ config/
│   └─ default.yaml             ← 데이터 경로·스크립트 위치·파라미터를 한 곳에서 관리
│
├─ src/
│   ├─ text_cleaner.py               ← 텍스트 정제
│   ├─ sentence_splitter.py      ← 문장 단위 분리
│   ├─ [sentiment.py](http://sentiment.py/)                   ← KcELECTRA 감성 분류
│   ├─ keyword_classifier.py    ← 키워드 멀티레이블 분류
│   └─ [total.py](http://total.py/)                              ← 위 4단계를 순차 실행하는 오케스트레이터
│
├─ Data/

│   └─ intermediate/

│        ├─step1_clean.csv

│        ├─step2_split.csv

│        ├─step3_sentiment.csv
│   └─ test_data_final.csv      ← 파이프라인 입력 데이터

│   └─ test_data_final_processed.csv      ← 파이프라인 실행 후 결과 csv
│
└─ Bert_model_beomi_KcELECTRA-base-v2022_maxlen_64/  ← 로컬 모델 사용 시에만 필요
├─ config.json              ← 모델 설정
├─ vocab.txt                ← 토크나이저 사전
├─ tf_model.h5              ← 학습된 가중치
└─ special_tokens_map.json, tokenizer_config.json



## ⚙️ 설치 및 실행
1. 의존성 설치  
   ```bash
   pip install -r requirements.txt

  2. config/default.yaml 여기에 파라미터랑 인풋 아웃풋 경로 다 수정가능
  3. 전체 파이프라인 실행
     python NLP/total.py --config NLP/config/default.yaml
