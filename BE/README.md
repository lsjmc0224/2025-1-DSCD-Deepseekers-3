# DSCD Deepseekers BE 서버

## 개요
이 서버는 다양한 소셜/커뮤니티/동영상 플랫폼(YouTube, Instiz, TikTok 등)에서 데이터를 수집하고, 수집된 데이터를 분석하는 백엔드 시스템입니다. 데이터 수집, 저장, 분석, 결과 제공까지의 전 과정을 담당합니다.

---

## 데이터베이스 구조

### 1. 수집 부분
- **Keywords**: 수집에 사용된 키워드 및 검색 시각을 저장합니다.
- **Youtube/Instiz/Tiktok 등 각 플랫폼별 원본 데이터 테이블**: 영상, 게시글, 댓글 등 원본 데이터를 저장합니다.
- **Collected 테이블**: 각 원본 데이터와 키워드의 관계, 실제 수집 시각을 기록합니다. (예: CollectedYoutubeComments, CollectedInstizPosts 등)
- **수집 부분 ERD**

![수집 부분 ERD](asset/수집 부분 ERD.png)


### 2. 분석 부분
- **Sentiments, Aspects**: 감성/속성 분류 기준 테이블입니다.
- **AnalysisLogs, ContentAnalyses**: 분석 작업의 로그와, 각 문장/컨텐츠별 분석 결과를 저장합니다.
- **분석 부분 ERD**

![분석 부분 ERD](asset/분석 부분 ERD.png)

---

## 기타
- 모든 테이블 구조 및 관계는 ERD를 참고하세요.
- 자세한 모델 설명은 `app/models/` 폴더의 각 파일에 주석으로 포함되어 있습니다.
