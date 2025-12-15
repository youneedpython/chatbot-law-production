from fastapi import FastAPI
from pydantic import BaseModel
from app.service.llm_service import generate_answer


app = FastAPI(title='chatbot-law-production')

class ChatRequet(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/chat', response_model=ChatResponse)
def chat(request: ChatRequet):
    answer = generate_answer(request.message)
    return ChatResponse(answer=answer)


