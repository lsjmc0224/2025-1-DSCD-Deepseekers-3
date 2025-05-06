"""
테이블 생성 SQL 스크립트 생성기

SQLAlchemy 모델로부터 테이블 생성 SQL을 생성하고 파일로 저장합니다.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 경로 설정 및 인쇄
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"현재 디렉토리: {current_dir}")
sys.path.insert(0, current_dir)
print(f"파이썬 경로: {sys.path}")

try:
    # 모델 임포트 테스트
    print("모듈 임포트 시도...")
    from app.db.base import Base
    print("Base 클래스 임포트 성공")
    
    # 데이터베이스 URL 설정
    pg_url = os.environ.get("DATABASE_URL")
    print(f"원본 DATABASE_URL: {pg_url}")
    
    if pg_url and "+asyncpg" in pg_url:
        # asyncpg를 psycopg2로 변경 (동기식 드라이버 필요)
        pg_url = pg_url.replace("+asyncpg", "")
    
    if not pg_url:
        pg_user = os.environ.get("POSTGRES_USER")
        pg_pwd = os.environ.get("POSTGRES_PASSWORD")
        pg_server = os.environ.get("POSTGRES_SERVER")
        pg_db = os.environ.get("POSTGRES_DB")
        
        print(f"POSTGRES_USER: {pg_user}")
        print(f"POSTGRES_SERVER: {pg_server}")
        print(f"POSTGRES_DB: {pg_db}")
        
        if all([pg_user, pg_pwd, pg_server, pg_db]):
            pg_url = f"postgresql://{pg_user}:{pg_pwd}@{pg_server}/{pg_db}"
        else:
            raise Exception("데이터베이스 연결 정보가 필요합니다. DATABASE_URL 또는 POSTGRES_* 환경 변수를 설정하세요.")
    
    print(f"사용할 데이터베이스 URL: {pg_url}")
    
    # 모델 및 데이터베이스 설정 로드
    try:
        from app.models.youtube_data import YouTubeVideo, YouTubeComment, YouTubeSentimentAnalysis, CollectionJob
        print("YouTube 데이터 모델 임포트 성공")
    except Exception as e:
        print(f"YouTube 데이터 모델 임포트 실패: {e}")
        # 트레이스백 출력
        import traceback
        traceback.print_exc()
    
    # SQLAlchemy 엔진 생성
    from sqlalchemy import create_engine
    engine = create_engine(pg_url)
    
    # 테이블 정보 추출
    try:
        metadata = Base.metadata
        tables = list(metadata.sorted_tables)
        print(f"테이블 수: {len(tables)}")
        for table in tables:
            print(f"테이블: {table.name}")
    except Exception as e:
        print(f"메타데이터 처리 중 오류: {e}")
    
    # SQL 파일 저장 디렉토리
    sql_dir = Path("migrations/sql")
    sql_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 테이블 생성 SQL 추출
        create_tables_sql = []
        drop_tables_sql = []
        
        # 모든 테이블에 대한 CREATE TABLE 문 생성
        for table in metadata.sorted_tables:
            create_sql = str(table.create(bind=engine).compile()).strip() + ";"
            create_tables_sql.append(create_sql)
            drop_tables_sql.insert(0, f"DROP TABLE IF EXISTS {table.name} CASCADE;")
        
        # SQL 파일 생성
        create_sql_path = sql_dir / "create_tables.sql"
        with open(create_sql_path, "w", encoding="utf-8") as f:
            f.write("-- 테이블 생성 SQL\n\n")
            f.write("\n\n".join(create_tables_sql))
        
        drop_sql_path = sql_dir / "drop_tables.sql"
        with open(drop_sql_path, "w", encoding="utf-8") as f:
            f.write("-- 테이블 삭제 SQL\n\n")
            f.write("\n".join(drop_tables_sql))
        
        print(f"테이블 생성 SQL이 생성되었습니다: {create_sql_path}")
        print(f"테이블 삭제 SQL이 생성되었습니다: {drop_sql_path}")
    except Exception as e:
        print(f"SQL 생성 중 오류: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"스크립트 실행 중 오류: {e}")
    import traceback
    traceback.print_exc()

# 데이터베이스 연결 테스트
try:
    conn = engine.connect()
    print("데이터베이스에 성공적으로 연결되었습니다.")
    conn.close()
except Exception as e:
    print(f"데이터베이스 연결에 실패했습니다: {e}")
    print("자동으로 테이블을 생성하지 않습니다. SQL 파일을 수동으로 실행하세요.")
else:
    # 데이터베이스에 테이블 생성 여부 확인
    create_tables = input("데이터베이스에 테이블을 생성하시겠습니까? (y/n): ")
    if create_tables.lower() == 'y':
        try:
            Base.metadata.create_all(engine)
            print("테이블이 성공적으로 생성되었습니다.")
        except Exception as e:
            print(f"테이블 생성 중 오류가 발생했습니다: {e}")
    else:
        print("테이블 생성이 취소되었습니다.") 