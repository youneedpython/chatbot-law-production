"""
routers/chat.py

채팅 응답 생성용 엔드포인트 라우터 (v0.4.1 기준)

엔드포인트
- POST /chat/{session_id}
  1) 사용자 메시지 DB 저장(repository.append_message)
  2) LLM 응답 생성(service.ask_llm)
  3) 어시스턴트 메시지 DB 저장(repository.append_message)
  4) answer 반환

원칙
- 라우터는 HTTP/검증/저장/응답만 담당
- LLM 호출 및 프롬프트 구성은 service 계층에서만 처리
"""


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.repository.chat import append_message
from app.schemas.chat_request import ChatRequest
from app.service.llm_service import ask_llm


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
    answer, _ = ask_llm(db=db, message=payload.message, session_id=session_id)

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
