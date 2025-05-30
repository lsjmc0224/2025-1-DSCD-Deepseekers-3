# NLP 파이프라인 프로젝트

## 📁 디렉터리 구조
kcelectra-base-DC/
├─ config/
│   └─ default.yaml # 설정을 한 곳에서 관리 data, path, 파라미터 모두 여기서 조정
├─ src/
│   ├─ text_cleaner.py
│   ├─ sentence_splitter.py
│   ├─ sentiment.py
│   ├─ keyword_classifier.py
│   └─ total.py
├─ Data/
│   └─ test_data_final.csv
----------------------------------- 로컬에서 저장된 거 쓰는 경우에만 아래 파일 필요
└─ Bert_model_beomi_KcELECTRA-base-v2022_maxlen_64/
    ├─ config.json
    ├─ vocab.txt
    ├─ tf_model.h5
    └─ …



## ⚙️ 설치 및 실행
1. 의존성 설치  
   ```bash
   pip install -r requirements.txt

  2. config/default.yaml 여기에 파라미터랑 인풋 아웃풋 경로 다 수정가능
  3. 전체 파이프라인 실행
     python NLP/total.py --config NLP/config/default.yaml
