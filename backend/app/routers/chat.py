"""
routers/chat.py

채팅 응답 생성용 엔드포인트 라우터 (v0.4.0 기준)

엔드포인트
- POST /chat/{session_id}
  1) 사용자 메시지 저장(repository.append_message)
  2) LLM 호출(call_llm)
  3) 어시스턴트 메시지 저장(repository.append_message)
  4) answer 반환

현재 상태
- call_llm()은 라우터 내부에 임시/직접 구현되어 있음(OpenAI SDK 사용)
- v0.4.1에서는 call_llm을 service 계층으로 분리하여
  비즈니스 로직과 HTTP 레이어를 분리하는 것이 목표
"""


import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI

from app.db import get_db
from app.repository.chat import append_message
from app.schemas.chat_request import ChatRequest
from app.service.llm_service import ask_llm

from app.core.config import OPENAI_API_KEY, OPENAI_MODEL


client = OpenAI(api_key=OPENAI_API_KEY)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("/{session_id}")
def chat(
    session_id: str,
    payload: ChatRequest,
    db: Session = Depends(get_db),
):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="message is empty")

    ## 1. user 메시지 저장
    append_message(
        db=db,
        conversation_id=session_id,
        role="user",
        content=payload.message,
    )

    ## 2. LLM 호출 (service로 위임)
    answer, _ = ask_llm(message=payload.message, session_id=session_id)

    ## 3. assistant 메시지 저장
    append_message(
        db=db,
        conversation_id=session_id,
        role="assistant",
        content=answer,
    )

    ## 4. 응답 반환
    return {
        "session_id": session_id,
        "answer": answer,
    }
