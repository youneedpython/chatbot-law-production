"""
routers/chat.py
- v0.4.0 /chat/{session_id}
- History API를 사용하는 오케스트레이션 엔드포인트
"""


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.repository.chat import append_message
from app.schemas.chat_request import ChatRequest


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


def call_llm(user_message: str) -> str:
    """
    실제 서비스에서는 여기서 OpenAI / LLM 호출
    지금은 예시용 더미 구현
    """
    ## TODO: 기존 LLM 호출 코드 이곳으로 이동
    return f'네, 질문 주신 내용에 대해 안내드리겠습니다.\n\n({user_message})'


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

    ## 2. 호출
    answer = call_llm(payload.message)

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
