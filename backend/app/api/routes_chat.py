"""
########################################################################
routes_chat.py

FastAPI Chat API 라우터 정의 파일입니다.

역할:
- 전세사기 피해 상담 챗봇의 HTTP API 엔드포인트를 정의합니다.
- 클라이언트(Frontend)로부터 질문을 받아 LLM 서비스 계층에 전달하고,
  그 결과를 JSON 형태로 반환합니다.

제공 API:
- GET  /health : 서버 상태 확인용 헬스체크 엔드포인트
- POST /chat   : 사용자 질문을 받아 LLM 답변을 생성하는 핵심 API

설계 원칙:
- 이 파일은 '요청/응답 처리'만 담당합니다.
- 실제 LLM 호출 로직은 app.service.llm_service 에 위임합니다.
- 비즈니스 로직과 API 계층을 분리하여 유지보수성을 높입니다.
########################################################################
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.service.llm_service import ask_llm


router = APIRouter()

class ChatRequet(BaseModel):
    """
    채팅 요청 데이터 모델

    - message: 사용자 입력 질문
    - session_id: (확장용) 대화 세션 식별자
    """
    message: str
    session_id: str | None = None


@router.get('/health')
def health():
    """
    헬스체크 API
    - 서버가 정상 동작 중인지 확인
    """
    return {
        'status': 'ok',
        'service': 'chatbot-law-backend',
    }

@router.post('/chat')
def chat(request: ChatRequet):
    """
    챗봇 질의 API
    - 사용자 질문을 받아 LLM 응답을 반환
    """
    try:
        answer, session_id = ask_llm(request.message, request.session_id)
        return {
            'answer': answer, 
            'session_id': session_id
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail='Failed to generate answer from LLM'
        )