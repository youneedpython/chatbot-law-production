"""
init_db.py
- 개발용: 테이블 생성 스크립트
- 실행 위치: backend/
- DATABASE_URL 기준으로 sqlite DB 파일 생성
"""


from app.db import engine
from app.models.base import Base
from app.models import chat  # noqa: F401 (모델 import로 메타데이터 등록)


def main():
    print(f"Using database: {engine.url}")
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")


if __name__=="__main__":
    main()