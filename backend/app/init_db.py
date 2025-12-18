"""
init_db.py
- 개발용: 테이블 생성
"""


from app.db import engine
from app.models.base import Base
from app.models import chat  # noqa: F401 (모델 import로 메타데이터 등록)


Base.metadata.create_all(bind=engine)
print("Database tables created.")