"""
데이터베이스 기본 모델 정의

이 모듈은 SQLAlchemy ORM 모델의 기본 클래스와 공통 함수를 제공합니다.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Annotated

from sqlalchemy import Column, DateTime, String, create_engine
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    """
    모든 SQLAlchemy 모델에 대한 기본 클래스
    
    이 클래스는 모든 모델에 공통적인 속성과 메서드를 제공합니다.
    - id: UUID 기반 기본 키
    - created_at: 레코드 생성 시간
    - updated_at: 레코드 업데이트 시간
    - __tablename__: 클래스 이름 기반의 테이블 이름
    """
    __allow_unmapped__ = True  # 기존 방식의 Column 정의 허용
    
    # 모든 모델에 공통 컬럼 정의
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 자동으로 테이블 이름 생성
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        클래스 이름을 snake_case로 변환하여 테이블 이름 생성
        예: UserProfile -> user_profile
        """
        return cls.__name__.lower()

    def to_dict(self) -> Dict[str, Any]:
        """
        모델 인스턴스를 딕셔너리로 변환
        
        Returns:
            Dict[str, Any]: 모델 속성을 포함하는 딕셔너리
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


ModelType = TypeVar("ModelType", bound=Base)
"""SQLAlchemy 모델 타입 변수"""


# Make sure all models are imported and have their metadata registered
# before creating tables
def get_metadata():
    """
    데이터베이스 테이블 생성에 필요한 메타데이터를 모두 반환합니다.
    """
    return [Base.metadata] 