FROM python:3.10-slim

WORKDIR /app

# 의존성 설치 (캐싱 활용을 위해 요구사항 파일을 먼저 복사)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# KoNLPy 및 Java 설치 (NLP 작업에 필요)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    g++ \
    default-jdk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 포트 설정
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 