from fastapi import FastAPI
from app.routers import history


app = FastAPI(title="Chatbot Law API")

app.include_router(history.router)
