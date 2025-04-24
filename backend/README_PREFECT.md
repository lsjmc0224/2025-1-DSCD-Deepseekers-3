# Prefect 파이프라인 활용 가이드

SNATCH 프로젝트의 Prefect 파이프라인 설정, 실행 및 모니터링을 위한 가이드입니다.

## 사전 요구사항

- Python 3.8 이상
- Prefect 2.0 이상 설치: `pip install prefect>=2.0.0`
- 필요한 추가 패키지: `httpx`

## 주요 스크립트

모든 스크립트는 `backend/scripts` 디렉토리에 위치해 있습니다.

### 1. Prefect 설정 (`prefect_setup.py`)

Prefect 서버 연결 및 워크플로우 배포를 설정합니다.

```bash
# 기본 설정
python scripts/prefect_setup.py

# 에이전트 시작과 함께 설정
python scripts/prefect_setup.py --start-agent
```

### 2. YouTube 파이프라인 실행 (`run_youtube_pipeline.py`)

YouTube ETL 파이프라인을 직접 실행합니다.

```bash
# 기본 설정으로 실행
python scripts/run_youtube_pipeline.py

# 커스텀 설정으로 실행
python scripts/run_youtube_pipeline.py --max-videos 5 --max-comments 200

# 키워드 검색만 실행
python scripts/run_youtube_pipeline.py --keywords-only

# 크리에이터 채널만 수집
python scripts/run_youtube_pipeline.py --creators-only

# 전처리 단계 건너뛰기
python scripts/run_youtube_pipeline.py --skip-preprocessing
```

### 3. Prefect 모니터링 (`monitor_prefect.py`)

Prefect 워크플로우 및 실행 상태를 모니터링합니다.

```bash
# 서버 및 워크플로우 상태 확인
python scripts/monitor_prefect.py status

# 플로우 실행 기록 조회
python scripts/monitor_prefect.py runs
python scripts/monitor_prefect.py runs --limit 20
python scripts/monitor_prefect.py runs --status COMPLETED
python scripts/monitor_prefect.py runs --flow "youtube-etl"

# 실행 기록을 파일로 저장
python scripts/monitor_prefect.py runs --save
python scripts/monitor_prefect.py runs --save --output "data/flow_runs.json"

# 배포 목록 조회
python scripts/monitor_prefect.py deployments
python scripts/monitor_prefect.py deployments --flow "youtube"
python scripts/monitor_prefect.py deployments --tag "youtube" --tag "etl"

# 실행 로그 조회
python scripts/monitor_prefect.py logs <flow_run_id>

# 연속 모니터링
python scripts/monitor_prefect.py watch
python scripts/monitor_prefect.py watch --interval 10
python scripts/monitor_prefect.py watch --count 5
```

## 유틸리티 함수

`backend/utils/prefect_utils.py` 모듈에는 Prefect 관련 유틸리티 함수들이 포함되어 있습니다:

- 플로우 실행 기록 조회
- 배포 상세 정보 조회
- 배포 스케줄 일시 중지/재개
- 즉시 실행 명령
- 로그 조회
- 서버 상태 확인

이 모듈을 직접 실행하면 현재 Prefect 서버 상태를 확인할 수 있습니다:

```bash
python -m utils.prefect_utils
```

## 파이프라인 구조

SNATCH 프로젝트의 YouTube ETL 파이프라인은 다음 단계로 구성됩니다:

1. **데이터 수집**
   - 키워드 기반 YouTube 동영상 검색
   - 인기 크리에이터 채널 동영상 수집
   - 비디오 메타데이터, 댓글, 자막 수집

2. **데이터 전처리**
   - 댓글 텍스트 전처리
   - 중복 제거 및 정제

3. **키워드 추출**
   - 전처리된 댓글에서 주요 키워드 추출
   - 감성 분석 및 토픽 모델링

4. **데이터베이스 저장**
   - 수집 및 분석된 데이터 저장
   - 통계 및 요약 정보 생성

## 문제 해결

1. **Prefect 서버 연결 문제**

   ```bash
   # Prefect API URL 확인
   prefect config view

   # API URL 설정
   prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
   ```

2. **워크 풀 문제**

   ```bash
   # 워크 풀 목록 확인
   prefect work-pool ls

   # 워크 풀 생성
   prefect work-pool create sweetspot-pool --type process
   ```

3. **에이전트 실행 문제**

   ```bash
   # 에이전트 직접 시작
   prefect agent start -p sweetspot-pool
   ```

4. **로깅 및 디버깅**

   - 파이프라인 실행 시 로그는 기본적으로 `~/.prefect/flows` 디렉토리에 저장됩니다.
   - 자세한 로그는 Prefect UI 또는 `logs` 명령으로 확인할 수 있습니다. 