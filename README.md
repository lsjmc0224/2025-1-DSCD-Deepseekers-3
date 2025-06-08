# 2025-1-DSCD-Deepseekers-3
2025-1학기 데이터사이언스연계전공 3팀 Deepseekers 레포지토리입니다.

# 시연 동영상
https://www.youtube.com/watch?v=kX44fCQQjFY

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
