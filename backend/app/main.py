"""
app/main.py

FastAPI 애플리케이션 엔트리 포인트

역할
- FastAPI 앱 객체 생성
- 라우터(chat, history, health) 등록 및 API prefix 구성
  - /api/chat/...
  - /api/conversations/...
  - /health

운영 참고
- 배포 환경(uvicorn/gunicorn, EB 등)에서 이 모듈의 app 객체를 로드하여 실행
"""


from fastapi import FastAPI
from app.routers import chat, history, health


app = FastAPI(title="Chatbot Law API")

app.include_router(chat.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(health.router)