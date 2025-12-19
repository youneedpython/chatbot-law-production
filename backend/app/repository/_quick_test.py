"""
repository/_quick_test.py

repository.chat 모듈의 CRUD 동작을 빠르게 검증하기 위한 로컬 테스트 스크립트.

주요 검증 포인트
- SessionLocal로 DB 연결이 정상인지
- append_message()가 seq를 자동 증가시키며 저장하는지
- list_messages()가 limit/정렬 규칙에 맞게 반환하는지

사용 범위
- 개발/디버깅 목적의 수동 실행 스크립트
- 운영 환경에서는 실행하지 않음
"""


from app.db import SessionLocal
from app.repository.chat import append_message, list_messages


db = SessionLocal()

sid = "test-session-001"
append_message(db, sid, "user", "정부지원도 있나요?")
append_message(db, sid, "assistant", "네, 주요 지원은 ...")

msgs = list_messages(db, sid, limit=50)

for m in msgs:
    print(m.seq, m.role, m.content)

db.close()