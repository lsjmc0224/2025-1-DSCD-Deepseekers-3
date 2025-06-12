# 2025-1-DSCD-Deepseekers-3
2025-1학기 데이터사이언스연계전공 3팀 Deepseekers 레포지토리입니다.

# 시연 동영상
https://www.youtube.com/watch?v=kX44fCQQjFY

#NLP
편의점 디저트 리뷰 데이터 전처리 → 문장 분리 → 감성 분류 → 키워드 멀티레이블 분류를 모듈화하고,  
`total.py`로 한 번에 실행 가능한 end-to-End NLP 파이프라인입니다.  
학습된 KcELECTRA 모델 체크포인트는 Hugging Face Hub에, 코드와 설정은 GitHub에 공개되어 있어 누구나 쉽게 재현·확장할 수 있습니다.

kcelectra-base-DC/ # GitHub·Hugging Face 공통 루트

자세한 파이프라인은 NLP폴더 내 readme에 첨부하였습니다.
---

## ⚙️ 설치 및 실행

1. **레포지터리 클론**  
   git clone https://github.com/your-username/kcelectra-base-DC.git
   cd kcelectra-base-DC
   
3. 의존성 설치
pip install -r requirements.txt

4. config/default.yaml 수정
data.input_csv, data.intermediate_dir, data.output_csv
paths.scripts_dir, paths.model_dir (허브 레포 ID 혹은 로컬 경로)
sentiment.max_length, sentiment.batch_size 등

5. 전체 파이프라인 실행
python src/total.py --config config/default.yaml


🚀 Hugging Face Hub 연동
from transformers import ElectraTokenizer, TFElectraForSequenceClassification
repo_id = "alsxxxz/kcelectra-base-DC"
tokenizer = ElectraTokenizer.from_pretrained(repo_id)
model     = TFElectraForSequenceClassification.from_pretrained(repo_id, num_labels=2)



## 0. how to start (BE, DA)
1. `python 3.12` 설치
2. bash에서 가상환경 / 패키지 설치하기
```bash
# bash에서 아래스크립트 기입
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

## 1. how to do DA

#### tiktok scrapping
1. video_scrapper.py에서 TARGET_URL 같은방식으로 설정 (지금 적힌 내용은 밤티라미수 tiktok을 검색한 결과 중, 짧은 동영상 탭 검색결과임)
2. tiktok-comment-scrapper 폴더 경로로 이동
```bash
cd DA
```
3. tiktok 영상 댓글 scrapping
```bash
python video_scrapper.py
python comment_scrapper.py
python preprocess.py
```
4. DA/data 폴더에서 파일 확인
   
