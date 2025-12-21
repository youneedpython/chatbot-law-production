"""
app/db.py

SQLAlchemy 엔진/세션(SessionLocal) 생성과 FastAPI 의존성 주입(get_db)을 제공하는 DB 설정 모듈

주요 역할
- DATABASE_URL 환경변수 기반으로 DB 엔진 생성 (기본: sqlite:///./test.db)
- SessionLocal(sessionmaker) 생성
- FastAPI Depends로 사용할 get_db() 제너레이터 제공 (요청 단위 세션 열고 닫기)

주의
- .env 로딩은 app.core.config에서만 수행
- 이 모듈은 환경변수를 직접 로드하지 않고, config 값을 import하여 사용
"""


from __future__ import annotations

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL


## SQLite는 check_same_thread 옵션이 필요합니다.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()