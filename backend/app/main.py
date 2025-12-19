from fastapi import FastAPI
from app.routers import chat, history, health


app = FastAPI(title="Chatbot Law API")

app.include_router(chat.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(health.router)