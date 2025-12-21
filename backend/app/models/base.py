"""
models/base.py

SQLAlchemy ORM 모델에서 공통으로 사용하는 Declarative Base 정의 파일.

역할:
- SQLAlchemy 2.0 스타일(DeclarativeBase)을 사용하는 모든 ORM 모델의
  공통 부모 클래스(Base)를 제공합니다.
- metadata, table 생성, session 연동의 기준이 됩니다.

설계 원칙:
- 모든 ORM 모델은 반드시 이 Base를 상속해야 합니다.
- 모델 간 공통 로직은 이 파일에 두지 않고,
  순수 Base 정의 역할만 담당합니다.
"""


from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass