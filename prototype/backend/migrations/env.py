import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

# FastAPI 앱 모델 파일 임포트
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.base import Base  # noqa
from app.models.youtube_data import YouTubeVideo, YouTubeComment, YouTubeSentimentAnalysis

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# URL 설정 - 환경 변수에서 가져옴
pg_url = os.environ.get("DATABASE_URL")
if pg_url and "+asyncpg" in pg_url:
    # asyncpg를 psycopg2로 변경 (Alembic은 동기식 드라이버 필요)
    pg_url = pg_url.replace("+asyncpg", "")

if not pg_url:
    pg_user = os.environ.get("POSTGRES_USER")
    pg_pwd = os.environ.get("POSTGRES_PASSWORD")
    pg_server = os.environ.get("POSTGRES_SERVER")
    pg_db = os.environ.get("POSTGRES_DB")
    
    if all([pg_user, pg_pwd, pg_server, pg_db]):
        pg_url = f"postgresql://{pg_user}:{pg_pwd}@{pg_server}/{pg_db}"
    else:
        raise Exception("데이터베이스 연결 정보가 필요합니다. DATABASE_URL 또는 POSTGRES_* 환경 변수를 설정하세요.")

# alembic.ini의 sqlalchemy.url 값을 환경 변수에서 가져온 값으로 대체
config.set_main_option("sqlalchemy.url", pg_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,  # 타입 변경 감지
            compare_server_default=True,  # 기본값 변경 감지
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
