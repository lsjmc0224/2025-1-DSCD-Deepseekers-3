FROM node:16-alpine

WORKDIR /app

# 의존성 설치 (캐싱 활용을 위해 package.json을 먼저 복사)
COPY package.json package-lock.json* ./
RUN npm install

# 애플리케이션 코드 복사
COPY . .

# 포트 설정
EXPOSE 3000

# 개발 서버 실행
CMD ["npm", "run", "dev"] 