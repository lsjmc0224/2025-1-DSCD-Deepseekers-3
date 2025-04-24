# SNATCH 프로젝트 가이드

SNATCH 프로젝트는 YouTube와 같은 소셜 미디어에서 데이터를 수집하고 분석하는 파이프라인을 구축하는 프로젝트입니다.

## 프로젝트 구조

```
backend/
├── app/               # 애플리케이션 코드
│   ├── core/          # 핵심 설정 및 유틸리티
│   ├── db/            # 데이터베이스 설정
│   ├── models/        # 데이터 모델
│   └── services/      # 서비스 로직
│       ├── analyzers/ # 데이터 분석 서비스
│       ├── collectors/ # 데이터 수집 서비스
│       └── processors/ # 데이터 처리 서비스
├── pipelines/         # ETL 파이프라인
├── scripts/           # 유틸리티 스크립트
└── utils/             # 공통 유틸리티
```

## 시작하기

### 1. 환경 설정

먼저 필요한 패키지를 설치하고 환경을 설정합니다.

```bash
# 프로젝트 디렉토리로 이동
cd backend

# 통합 시작 스크립트 실행 (환경 설정만)
python scripts/start_project.py --setup-only
```

### 2. API 키 설정

`.env` 파일에 YouTube API 키를 설정합니다. `.env.example` 파일을 복사하여 `.env` 파일을 생성할 수 있습니다.

```
YOUTUBE_API_KEY=your_youtube_api_key_here
```

YouTube API 키 발급 방법:
1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성
3. YouTube Data API v3 활성화
4. API 키 생성

### 3. Prefect 서버 시작

Prefect 서버를 시작하고 워크플로우를 설정합니다.

```bash
# Prefect 서버 시작 및 워크플로우 설정
python scripts/setup_prefect_server.py --start-server
```

다른 터미널에서:

```bash
# 워크플로우 설정
python scripts/prefect_setup.py
```

### 4. 파이프라인 실행

YouTube ETL 파이프라인을 실행합니다.

```bash
# 기본 설정으로 파이프라인 실행
python scripts/run_youtube_pipeline.py

# 커스텀 설정으로 실행
python scripts/run_youtube_pipeline.py --max-videos 5 --max-comments 200
```

### 5. 통합 스크립트 사용 (한 번에 설정 및 실행)

모든 단계를 한 번에 설정하고 실행하려면:

```bash
# 모든 설정 및 파이프라인 실행
python scripts/start_project.py --run-pipeline
```

## 모니터링 및 관리

Prefect 워크플로우를 모니터링하고 관리하기 위한 도구를 제공합니다.

```bash
# 서버 및 워크플로우 상태 확인
python scripts/monitor_prefect.py status

# 실행 기록 조회
python scripts/monitor_prefect.py runs

# 배포 목록 조회
python scripts/monitor_prefect.py deployments

# 실시간 모니터링
python scripts/monitor_prefect.py watch
```

자세한 내용은 [Prefect 파이프라인 활용 가이드](README_PREFECT.md)를 참조하세요.

## 개발 가이드

개발 환경을 설정하려면:

```bash
# 개발용 패키지 설치
python scripts/install_requirements.py --dev
```

## 트러블슈팅

### YouTube API 할당량 초과

YouTube Data API는 일일 할당량이 제한되어 있습니다. 할당량을 초과하면 다음과 같은 오류가 발생할 수 있습니다:

```
HttpError 403: The request cannot be completed because you have exceeded your quota.
```

해결 방법:
- 다른 API 키 사용
- 할당량이 초기화될 때까지 기다리기 (보통 다음 날)
- Google Cloud Console에서 할당량 증가 요청

### Prefect 서버 연결 문제

Prefect 서버에 연결할 수 없는 경우:

```bash
# Prefect API URL 확인
prefect config view

# API URL 설정
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

## 추가 자료

- [Prefect 공식 문서](https://docs.prefect.io/)
- [YouTube Data API 문서](https://developers.google.com/youtube/v3/docs) 