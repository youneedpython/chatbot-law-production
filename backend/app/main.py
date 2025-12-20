from fastapi import FastAPI
from app.routers import chat, history


app = FastAPI(title="Chatbot Law API")

app.include_router(chat.router)
app.include_router(history.router)
