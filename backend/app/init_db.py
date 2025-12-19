"""
app/init_db.py

개발/테스트 환경에서 DB 테이블을 생성하는 초기화 스크립트

동작
- app.db.engine을 사용해 연결된 DB에 대해 Base.metadata.create_all() 수행
- app.models.chat 등을 import하여 모델 메타데이터를 등록한 뒤 테이블 생성

사용 방식
- backend/ 위치에서 python -m app.init_db 또는 python app/init_db.py 형태로 실행
- 운영 환경에서는 마이그레이션 도구(Alembic 등) 사용을 권장
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