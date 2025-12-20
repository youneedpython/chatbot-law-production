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