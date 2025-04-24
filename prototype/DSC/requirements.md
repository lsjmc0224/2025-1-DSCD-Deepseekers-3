# SNATCH 프로젝트 요구사항 문서

## 프로젝트 개요 (#project-overview)

SNATCH는 편의점 디저트 제품에 대한 고객 피드백을 자동으로 수집, 분석하고 시각화하는 VoC(Voice of Customer) 관리 시스템입니다. YouTube, 커뮤니티/포털, 인스타그램에서 데이터를 수집하여 감성 분석과 키워드 추출을 수행하고, 실시간 대시보드와 알림 시스템을 통해 마케팅 의사결정을 지원합니다.

### 주요 기술 스택
- **백엔드**: Python, FastAPI, Prefect, KoNLPy, LMKor-ELECTRA, YAKE!
- **데이터베이스**: PostgreSQL (GCP)
- **스토리지**: AWS S3
- **프론트엔드**: React.js, Recharts/D3.js
- **알림 시스템**: Slack/Email API
- **배포**: Docker, GCP

### 목표 지표
- 데이터 수집 정확도: 95% 이상
- 감성 분석 정밀도: 90% 이상
- 처리 속도: 수집부터 시각화까지 15분 이내
- 사용자 만족도: 80% 이상

## 기능 요구사항 (#feature-requirements)

### 1. 데이터 수집 모듈
- **YouTube API 연동**: 편의점 디저트 관련 리뷰 데이터를 수집
  - 영상 메타데이터 및 댓글 수집
  - 시청자 반응(좋아요 수, 조회수) 수집
  - 인기 푸드크리에이터의 리뷰 자동 추적
  
- **커뮤니티/포털 API 연동**: 네이버 카페, 다음 카페, 뽐뿌 등의 데이터 수집
  - 게시글 및 댓글 크롤링
  - 추천수, 조회수 등 반응 지표 수집
  
- **인스타그램 API 연동**: 편의점 디저트 해시태그 관련 게시물 수집
  - 이미지 메타데이터 및 태그 수집
  - 댓글 및 좋아요 수 수집

### 2. ETL 파이프라인
- **Prefect 워크플로우 구현**: 데이터 수집, 전처리, 분석, 저장 과정 자동화
  - 15분 주기의 데이터 수집 스케줄링
  - 오류 처리 및 재시도 메커니즘 구현
  - 데이터 파이프라인 모니터링

- **데이터 전처리**: 텍스트 정규화 및 클렌징
  - KoNLPy 활용 형태소 분석 및 토큰화
  - 불용어 제거 및 특수문자 처리
  - 편의점 디저트 관련 특화 용어 사전 구축 및 활용

### 3. 감성 분석 모듈
- **KR-BERT 기반 감성 분석**: 텍스트 데이터에서 감성 추출
  - 긍정/부정/중립 감성 분류
  - 감성 강도 측정 (5점 척도)
  - 편의점 디저트 리뷰에 특화된 모델 미세 조정

- **키워드 추출**: YAKE! 알고리즘을 활용한 핵심 키워드 추출
  - 맛, 가격, 패키징, 판매처, 식감, 재구매 의향 등 카테고리별 키워드 분류
  - 트렌드 및 이슈 탐지 알고리즘 구현

### 4. 데이터 저장 모듈
- **Raw 데이터 저장**: S3/Object Storage 활용
  - JSON 형식 데이터 저장
  - 파티션 및 버저닝 전략 구현
  - 데이터 백업 및 복구 메커니즘

- **분석 결과 저장**: PostgreSQL 기반 RDS 활용
  - 효율적인 시계열 데이터 저장 구조 설계
  - 인덱스 최적화를 통한 쿼리 성능 향상
  - 대시보드용 데이터 뷰 생성

### 5. 백엔드 API
- **FastAPI 기반 RESTful API**: 프론트엔드와 데이터 통신
  - 데이터 조회 및 필터링 엔드포인트
  - 실시간 데이터 갱신 지원
  - 인증 및 권한 관리 기능

- **Redis 캐싱 레이어**: 성능 최적화
  - 자주 요청되는 쿼리 결과 캐싱
  - 대시보드 로딩 시간 최소화

### 6. 프론트엔드 대시보드
- **React.js 기반 웹 애플리케이션**: 사용자 친화적 인터페이스
  - 반응형 디자인으로 모바일/데스크톱 지원
  - 컴포넌트 기반 아키텍처 설계
  - 상태 관리를 위한 Redux/Context API 활용

- **데이터 시각화**: Recharts/D3.js 활용
  - 감성 분석 결과 히트맵 구현
  - 트렌드 차트 및 시계열 데이터 시각화
  - 키워드 클라우드 구현
  - 이슈 타임라인 및 경쟁사 비교 차트

### 7. 알림 시스템
- **이벤트 기반 트리거**: 중요 이슈 감지 시 자동 알림
  - 부정적 키워드 급증 감지
  - 임계값 설정 및 관리 인터페이스
  - 알림 우선순위 설정 기능

- **다중 채널 알림**: Slack/Email 통합
  - 맞춤형 알림 템플릿 설계
  - 알림 히스토리 관리 기능
  - 수신자 그룹 설정 기능

### 8. 관리자 및 사용자 인터페이스
- **관리자 인터페이스**: 시스템 설정 및 관리
  - 데이터 소스 관리
  - 모니터링 대시보드 및 로그 검토
  - 사용자 권한 관리

- **사용자 인터페이스**: 맞춤형 분석 기능
  - 맞춤형 대시보드 설정
  - 리포트 생성 및 내보내기
  - 필터링 및 검색 기능

## 관련 코드 (#relevant-codes)

### 데이터 수집 예시 (YouTube API)
```python
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def fetch_youtube_comments(video_id, max_results=100):
    """
    YouTube 동영상의 댓글을 수집하는 함수
    
    Args:
        video_id (str): YouTube 동영상 ID
        max_results (int): 가져올 최대 댓글 수
    
    Returns:
        list: 댓글 목록
    """
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results
        )
        response = request.execute()
        
        comments = []
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'author': comment['authorDisplayName'],
                'text': comment['textDisplay'],
                'published_at': comment['publishedAt'],
                'like_count': comment['likeCount']
            })
            
        return comments
    
    except HttpError as e:
        print(f"YouTube API 오류 발생: {e}")
        return []
```

### ETL 파이프라인 예시 (Prefect)
```python
from prefect import task, flow
from prefect.task_runners import SequentialTaskRunner
import datetime

@task
def extract_data(source_type, params):
    """데이터 추출 태스크"""
    if source_type == "youtube":
        return fetch_youtube_comments(params["video_id"])
    elif source_type == "community":
        return fetch_community_posts(params["community_id"])
    elif source_type == "instagram":
        return fetch_instagram_posts(params["hashtag"])
    return []

@task
def transform_data(data):
    """데이터 전처리 태스크"""
    # 텍스트 정규화, 불용어 제거 등 전처리 작업
    processed_data = []
    for item in data:
        processed_item = preprocess_text(item)
        processed_data.append(processed_item)
    return processed_data

@task
def analyze_sentiment(data):
    """감성 분석 태스크"""
    results = []
    for item in data:
        sentiment = perform_sentiment_analysis(item["text"])
        keywords = extract_keywords(item["text"])
        results.append({
            "original": item,
            "sentiment": sentiment,
            "keywords": keywords
        })
    return results

@task
def load_data(results):
    """데이터 저장 태스크"""
    # 데이터베이스에 결과 저장
    store_to_database(results)
    return True

@flow(task_runner=SequentialTaskRunner())
def sweetspot_etl_pipeline(source_type, params):
    """SweetSpot ETL 파이프라인 플로우"""
    # 데이터 추출
    raw_data = extract_data(source_type, params)
    
    # 데이터 없으면 종료
    if not raw_data:
        return False
    
    # 데이터 전처리
    processed_data = transform_data(raw_data)
    
    # 감성 분석
    analysis_results = analyze_sentiment(processed_data)
    
    # 데이터 저장
    success = load_data(analysis_results)
    
    return success
```

### 감성 분석 예시 (KR-BERT)
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

class SentimentAnalyzer:
    def __init__(self, model_name="snunlp/KR-Medium"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
        
    def analyze(self, text):
        """
        텍스트의 감성을 분석하여 긍정/부정/중립 점수를 반환
        
        Args:
            text (str): 분석할 텍스트
            
        Returns:
            dict: 감성 분석 결과
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        scores = torch.softmax(outputs.logits, dim=1).numpy()[0]
        
        return {
            "positive": float(scores[2]),
            "neutral": float(scores[1]),
            "negative": float(scores[0]),
            "sentiment": ["negative", "neutral", "positive"][np.argmax(scores)],
            "confidence": float(np.max(scores))
        }
```

### 키워드 추출 예시 (YAKE!)
```python
import yake

class KeywordExtractor:
    def __init__(self, language="ko", max_ngram_size=3, deduplication_threshold=0.9):
        self.kw_extractor = yake.KeywordExtractor(
            lan=language,
            n=max_ngram_size,
            dedupLim=deduplication_threshold,
            top=20,
            features=None
        )
        
    def extract(self, text):
        """
        텍스트에서 핵심 키워드를 추출
        
        Args:
            text (str): 키워드를 추출할 텍스트
            
        Returns:
            list: 점수와 함께 추출된 키워드 목록
        """
        keywords = self.kw_extractor.extract_keywords(text)
        return [{"keyword": kw, "score": score} for kw, score in keywords]
    
    def categorize_keywords(self, keywords):
        """
        추출된 키워드를 카테고리별로 분류
        
        Args:
            keywords (list): 추출된 키워드 목록
            
        Returns:
            dict: 카테고리별로 분류된 키워드
        """
        categories = {
            "taste": [],      # 맛 관련
            "price": [],      # 가격 관련
            "packaging": [],  # 패키징 관련
            "store": [],      # 판매처 관련
            "repurchase": [], # 재구매 의향 관련
            "other": []       # 기타
        }
        
        # 카테고리별 키워드 분류 로직 구현
        for kw in keywords:
            # 여기에 분류 로직 구현
            pass
            
        return categories
```

### 프론트엔드 컴포넌트 예시 (React.js)
```jsx
import React, { useState, useEffect } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const SentimentTrendChart = ({ productId, period }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchSentimentData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/sentiment/trend?productId=${productId}&period=${period}`);
        
        if (!response.ok) {
          throw new Error('데이터를 불러오는데 실패했습니다.');
        }
        
        const result = await response.json();
        setData(result.data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };
    
    fetchSentimentData();
  }, [productId, period]);
  
  if (loading) return <div>로딩중...</div>;
  if (error) return <div>에러: {error}</div>;
  if (data.length === 0) return <div>데이터가 없습니다.</div>;
  
  return (
    <div className="chart-container">
      <h3>감성 분석 트렌드</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="positive" stroke="#82ca9d" name="긍정" />
          <Line type="monotone" dataKey="neutral" stroke="#8884d8" name="중립" />
          <Line type="monotone" dataKey="negative" stroke="#ff8042" name="부정" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SentimentTrendChart;
```

## 현재 파일 구조 (#current-file-structure)

```
sweetspot/
├── README.md                # 프로젝트 개요 및 설치 가이드
├── requirements.md          # 프로젝트 요구사항 문서 (현재 문서)
├── .gitignore               # Git 무시 파일 목록
├── docker-compose.yml       # Docker 컴포즈 구성 파일
├── backend/                 # 백엔드 애플리케이션
│   ├── Dockerfile           # 백엔드 Docker 빌드 파일
│   ├── requirements.txt     # Python 패키지 의존성
│   ├── main.py              # FastAPI 애플리케이션 엔트리 포인트
│   ├── alembic/             # 데이터베이스 마이그레이션
│   ├── app/                 # 주요 애플리케이션 코드
│   │   ├── __init__.py      
│   │   ├── api/             # API 라우트
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/   # API 엔드포인트
│   │   │   └── deps.py      # 의존성 주입
│   │   ├── core/            # 핵심 설정 및 보안
│   │   │   ├── config.py    # 환경 설정
│   │   │   └── security.py  # 인증 및 보안
│   │   ├── db/              # 데이터베이스
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── models/          # 데이터베이스 모델
│   │   ├── schemas/         # Pydantic 스키마
│   │   └── services/        # 비즈니스 로직
│   │       ├── collectors/  # 데이터 수집기
│   │       ├── processors/  # 데이터 처리기
│   │       └── analyzers/   # 데이터 분석기
│   ├── pipelines/           # Prefect 파이프라인
│   │   ├── __init__.py
│   │   ├── youtube.py       # YouTube 데이터 파이프라인
│   │   ├── community.py     # 커뮤니티 데이터 파이프라인
│   │   └── instagram.py     # 인스타그램 데이터 파이프라인
│   └── tests/               # 백엔드 테스트
│       ├── __init__.py
│       ├── conftest.py
│       └── test_api/        # API 테스트
├── frontend/                # 프론트엔드 애플리케이션
│   ├── Dockerfile           # 프론트엔드 Docker 빌드 파일
│   ├── package.json         # NPM 패키지 정의
│   ├── public/              # 정적 파일
│   └── src/                 # React 애플리케이션 소스
│       ├── index.js         # 앱 엔트리 포인트
│       ├── App.js           # 메인 App 컴포넌트
│       ├── components/      # 재사용 컴포넌트
│       │   ├── charts/      # 차트 및 시각화 컴포넌트
│       │   ├── dashboard/   # 대시보드 컴포넌트
│       │   └── common/      # 공통 UI 컴포넌트
│       ├── pages/           # 페이지 컴포넌트
│       ├── services/        # API 서비스
│       ├── hooks/           # 커스텀 훅
│       ├── context/         # React 컨텍스트
│       ├── utils/           # 유틸리티 함수
│       └── styles/          # 스타일 파일
└── infra/                   # 인프라 구성
    ├── terraform/           # Terraform 인프라 코드
    ├── k8s/                 # Kubernetes 배포 파일
    └── scripts/             # 배포 및 유틸리티 스크립트
```

## 규칙 (#rules)

### 코드 스타일 규칙

#### 백엔드 (Python)
1. PEP 8 스타일 가이드를 준수합니다.
2. 클래스명은 PascalCase, 함수와 변수명은 snake_case를 사용합니다.
3. 모든 함수와 클래스에 독스트링(docstring)을 작성합니다.
4. 타입 힌팅을 최대한 활용합니다.
5. 예외 처리는 구체적으로 작성하고 로깅을 포함합니다.
6. 비동기 코드는 asyncio 패턴을 따릅니다.

#### 프론트엔드 (JavaScript/React)
1. ESLint와 Prettier 설정을 준수합니다.
2. 컴포넌트명은 PascalCase, 함수와 변수명은 camelCase를 사용합니다.
3. 컴포넌트는 가급적 함수형 컴포넌트와 Hooks를 사용합니다.
4. Props와 State의 타입은 PropTypes 또는 TypeScript를 통해 명시합니다.
5. 재사용 가능한 로직은 커스텀 Hooks로 분리합니다.
6. CSS-in-JS 또는 모듈형 CSS를 사용합니다.

### 아키텍처 규칙
1. **관심사 분리(Separation of Concerns)**: 각 모듈은 단일 책임을 가집니다.
2. **계층 아키텍처**: 데이터 접근, 비즈니스 로직, 프레젠테이션 계층을 분리합니다.
3. **의존성 주입**: 명시적 의존성 주입을 통해 결합도를 낮춥니다.
4. **API 설계**: RESTful 원칙을 준수하며, 일관된 응답 형식을 사용합니다.
5. **상태 관리**: 클라이언트 상태와 서버 상태를 명확히 구분합니다.

### 파일 및 폴더 구조 규칙
1. 기능별로 모듈화된 구조를 유지합니다.
2. 도메인별로 폴더를 구성하고, 공통 기능은 shared 또는 common 폴더에 배치합니다.
3. 테스트 파일은 대상 파일과 동일한 폴더에 위치시키거나, 별도의 tests 폴더에 동일한 구조로 배치합니다.
4. 설정 파일은 최상위 디렉토리에 배치합니다.
5. 환경별 설정은 .env 파일이나 환경변수를 통해 관리합니다.

### 데이터베이스 규칙
1. 모든 스키마 변경은 마이그레이션 도구(Alembic)를 통해 관리합니다.
2. 테이블 및 컬럼명은 snake_case를 사용합니다.
3. 외래 키는 {참조테이블명}_id 형식으로 명명합니다.
4. 인덱스는 성능을 고려하여 적절히 설정합니다.
5. 대용량 쿼리는 페이지네이션을 구현합니다.

### API 설계 규칙
1. 엔드포인트는 리소스를 명사로 표현하고, HTTP 메서드로 동작을 나타냅니다.
2. 응답은 일관된 형식({status, data, message})으로 반환합니다.
3. 오류 응답은 적절한 HTTP 상태 코드와 오류 메시지를 포함합니다.
4. API 버전은 URL 경로에 명시합니다 (예: /api/v1/...).
5. 인증이 필요한 엔드포인트는 JWT를 사용합니다.

### 배포 및 운영 규칙
1. 모든 환경 설정은 환경변수로 관리합니다.
2. CI/CD 파이프라인을 통해 자동화된 테스트와 배포를 진행합니다.
3. 로깅은 구조화된 형식으로 저장하고, 모니터링 도구와 연동합니다.
4. 백업 및 복구 전략을 문서화하고 정기적으로 테스트합니다.
5. 보안 업데이트를 정기적으로 적용합니다.

## 개발 프로세스 (#development-process)

### 개발 환경 설정
1. Docker Compose를 사용하여 로컬 개발 환경을 구성합니다.
2. 환경별(개발, 테스트, 운영) 설정 파일을 분리합니다.
3. 가상 데이터를 사용하여 개발 및 테스트를 진행합니다.

### 버전 관리 및 브랜치 전략
1. Git Flow 브랜치 모델을 따릅니다.
   - `main`: 프로덕션 환경 코드
   - `develop`: 개발 통합 브랜치
   - `feature/*`: 기능 개발 브랜치
   - `release/*`: 릴리즈 준비 브랜치
   - `hotfix/*`: 긴급 버그 수정 브랜치
2. 커밋 메시지는 Conventional Commits 규칙을 따릅니다.
3. Pull Request를 통한 코드 리뷰를 필수로 진행합니다.

### 테스트 전략
1. 단위 테스트: 개별 함수 및 컴포넌트의 기능 검증
2. 통합 테스트: 모듈 간 상호 작용 검증
3. E2E 테스트: 전체 시스템 흐름 검증
4. 성능 테스트: 부하 테스트 및 응답 시간 검증

### 배포 프로세스
1. 테스트 환경 배포 및 검증
2. QA 환경 배포 및 사용자 테스트
3. 스테이징 환경 배포 및 최종 검증
4. 프로덕션 환경 배포 (블루/그린 또는 카나리 배포 전략)
5. 모니터링 및 롤백 계획 준비

## 주요 마일스톤 및 일정 (#milestones)

### 1단계: 기초 인프라 및 데이터 수집 파이프라인 (1개월)
- 클라우드 인프라 구축
- 데이터 수집 API 연동
- ETL 파이프라인 기본 구조 개발
- 데이터 저장소 설계 및 구현

### 2단계: 분석 모델 및 백엔드 API 개발 (1개월)
- 텍스트 전처리 모듈 개발
- 감성 분석 모델 구현 및 최적화
- 키워드 추출 엔진 개발
- 백엔드 API 구현

### 3단계: 프론트엔드 및 알림 시스템 개발 (1개월)
- 대시보드 UI 구현
- 데이터 시각화 컴포넌트 개발
- 알림 시스템 구현
- 사용자 테스트 및 최적화

각 단계는 설계 → 개발 → 테스트 → 검증의 과정을 포함하며, 2주 단위로 진행 상황을 검토합니다.

## Cursor 활용 가이드 (#cursor-guide)

### Cursor에서 프로젝트 구현 시 유의사항

1. **코드 생성 요청 시 지침**
   - 구현할 기능의 요구사항을 명확히 설명합니다.
   - 관련된 파일 구조와 의존성을 언급합니다.
   - 예시: "YouTube API를 사용하여 데이터를 수집하는 collectors/youtube.py 파일을 구현해주세요."

2. **컨텍스트 활용**
   - 관련 코드 파일을 열어서 Cursor에게 컨텍스트를 제공합니다.
   - 특정 코드 블록에 대해 질문할 때는 해당 코드를 선택한 상태에서 요청합니다.
   - 예시: "이 감성 분석 함수에서 정확도를 개선할 방법을 제안해주세요."

3. **코드 리팩토링 요청**
   - 리팩토링 목적과 방향을 명확히 합니다.
   - 코드의 현재 문제점을 구체적으로 설명합니다.
   - 예시: "이 ETL 파이프라인 코드를 오류 처리와 로깅을 강화하는 방향으로 리팩토링해주세요."

4. **디버깅 지원 요청**
   - 오류 메시지와 스택 트레이스를 제공합니다.
   - 문제가 발생하는 상황을 자세히 설명합니다.
   - 예시: "이 API 호출 시 발생하는 429 오류를 해결하는 방법을 알려주세요."

### Cursor AI 활용 전략

1. **@requirements.md 활용**
   - 코드 생성을 요청할 때 "@requirements.md"를 언급하여 이 문서를 참조하도록 합니다.
   - 예시: "@requirements.md에 명시된 코드 스타일 규칙에 따라 키워드 추출 함수를 작성해주세요."

2. **부분적 구현 요청**
   - 대규모 코드보다는 모듈별로 나누어 구현을 요청합니다.
   - 예시: "데이터 수집 파이프라인의 YouTube 모듈부터 구현해주세요."

3. **검증 및 테스트 요청**
   - 구현된 코드에 대한 테스트 코드 작성을 요청합니다.
   - 예시: "이 감성 분석 함수에 대한 단위 테스트를 작성해주세요."

4. **문서화 요청**
   - 복잡한 로직이나 API에 대한 문서화를 요청합니다.
   - 예시: "이 ETL 파이프라인의 작동 방식을 설명하는 독스트링을 추가해주세요."

5. **단계적 개발**
   - 기본 기능을 먼저 구현한 후 점진적으로 개선하는 방식으로 요청합니다.
   - 예시: "먼저 기본적인 API 연결 기능을 구현하고, 그 다음에 오류 처리와 재시도 로직을 추가해주세요."

### 프로젝트 특화 지침

1. **데이터 파이프라인 개발**
   - Prefect 워크플로우는 명확한 입출력과 오류 처리를 포함해야 합니다.
   - 파이프라인의 각 단계는 독립적으로 테스트 가능하게 설계해야 합니다.

2. **NLP 모델 통합**
   - KR-BERT와 KoNLPy 통합 시 메모리 사용량과 처리 속도를 고려해야 합니다.
   - 모델 로딩은 애플리케이션 시작 시 한 번만 수행하도록 설계해야 합니다.

3. **API 개발**
   - FastAPI의 의존성 주입과 Pydantic 모델을 활용하여 견고한 API를 설계합니다.
   - 모든 API 엔드포인트는 적절한 오류 처리와 응답 형식을 가져야 합니다.

4. **프론트엔드 개발**
   - React 컴포넌트는 재사용성과 성능을 고려하여 설계합니다.
   - 상태 관리는 컨텍스트 API나 Redux를 일관되게 사용합니다.

## 참고 자료 및 링크 (#references)

### 기술 문서 및 튜토리얼
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Prefect 워크플로우 가이드](https://docs.prefect.io/)
- [KoNLPy 사용 가이드](https://konlpy.org/en/latest/)
- [Hugging Face Transformers 문서](https://huggingface.co/docs/transformers/index)
- [React.js 공식 문서](https://reactjs.org/docs/getting-started.html)

### 개발 도구
- [Poetry (Python 패키지 관리)](https://python-poetry.org/)
- [Black (Python 코드 포맷터)](https://black.readthedocs.io/)
- [ESLint (JavaScript 린터)](https://eslint.org/)
- [Prettier (코드 포맷터)](https://prettier.io/)

### 데이터 소스 API 문서
- [YouTube Data API](https://developers.google.com/youtube/v3/docs)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/)

### 모니터링 및 로깅
- [Prometheus](https://prometheus.io/docs/introduction/overview/)
- [Grafana](https://grafana.com/docs/)
- [ELK Stack](https://www.elastic.co/guide/index.html)

### 배포 및 인프라
- [Docker 문서](https://docs.docker.com/)
- [AWS 문서](https://docs.aws.amazon.com/)
- [Terraform 가이드](https://learn.hashicorp.com/terraform)