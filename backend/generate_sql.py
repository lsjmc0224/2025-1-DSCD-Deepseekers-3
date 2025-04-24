"""
테이블 SQL 생성 스크립트

SQLAlchemy 모델로부터 테이블 정의 SQL을 직접 생성합니다.
이 스크립트는 데이터베이스 연결이 없어도 작동합니다.
"""

import os
import sys
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    print("모델 임포트 시도...")
    from app.db.base import Base
    from app.models.youtube_data import YouTubeVideo, YouTubeComment, YouTubeSentimentAnalysis
    from app.models.collection_job import CollectionJob
    from sqlalchemy.schema import CreateTable, DropTable
    from sqlalchemy import create_engine
    
    print("모델 임포트 성공")

    # 더미 엔진 생성 (PostgreSQL 방언 사용)
    dummy_engine = create_engine("postgresql://", strategy="mock", executor=lambda *a, **kw: None)
    
    # SQL 파일 저장 디렉토리
    sql_dir = Path("migrations/sql")
    sql_dir.mkdir(parents=True, exist_ok=True)
    
    # 테이블 정보 확인
    metadata = Base.metadata
    tables = metadata.sorted_tables
    print(f"테이블 수: {len(tables)}")
    for table in tables:
        print(f"테이블: {table.name}")
    
    # SQL 생성
    create_tables_sql = []
    drop_tables_sql = []
    
    for table in tables:
        # 컴파일러에 dialect 전달 (PostgreSQL 방언)
        create_sql = str(CreateTable(table).compile(dialect=dummy_engine.dialect)) + ";"
        create_tables_sql.append(create_sql)
        
        drop_sql = f"DROP TABLE IF EXISTS {table.name} CASCADE;"
        drop_tables_sql.insert(0, drop_sql)
    
    # SQL 파일 작성
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
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc() 