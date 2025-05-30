# NLP 파이프라인 프로젝트

## 📁 디렉터리 구조
NLP/
├─ config/
│ └─ default.yaml
├─ src/
│ ├─ text_cleaner.py        코멘트 정제
│ ├─ sentence_splitter.py   문장 단위 분리
│ ├─ sentiment.py           감성 분류 
│ ├─ keyword_classifier.py  키워드 멀티레이블 분류
│ └─ total.py               1~4 단계 순차 실행
└─ README.md


## ⚙️ 설치 및 실행
1. 의존성 설치  
   ```bash
   pip install -r requirements.txt

  2. config/default.yaml 여기에 파라미터랑 인풋 아웃풋 경로 다 수정가능
  3. 전체 파이프라인 실행
     python NLP/total.py --config NLP/config/default.yaml
