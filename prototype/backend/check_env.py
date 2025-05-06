import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 데이터베이스 URL 확인
db_url = os.environ.get("DATABASE_URL")
print(f"DATABASE_URL={db_url}")

# PostgreSQL 설정 확인
pg_user = os.environ.get("POSTGRES_USER")
pg_pwd = os.environ.get("POSTGRES_PASSWORD")
pg_server = os.environ.get("POSTGRES_SERVER")
pg_db = os.environ.get("POSTGRES_DB")

print(f"POSTGRES_USER={pg_user}")
print(f"POSTGRES_PASSWORD={pg_pwd}")
print(f"POSTGRES_SERVER={pg_server}")
print(f"POSTGRES_DB={pg_db}")

# 환경 변수가 있을 경우 연결 문자열 생성
if all([pg_user, pg_pwd, pg_server, pg_db]):
    constructed_url = f"postgresql://{pg_user}:{pg_pwd}@{pg_server}/{pg_db}"
    print(f"Constructed URL: {constructed_url}")
else:
    print("일부 PostgreSQL 설정이 없어 연결 문자열을 생성할 수 없습니다.") 