"""
routers/chat.py
- v0.4.0 /chat/{session_id}
- History API를 사용하는 오케스트레이션 엔드포인트
"""

import os
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI

from app.db import get_db
from app.repository.chat import append_message
from app.schemas.chat_request import ChatRequest


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


def call_llm(user_message: str) -> str:
    """
    실제 서비스에서는 여기서 OpenAI / LLM 호출
    지금은 예시용 더미 구현
    """

    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": "당신은 전세사기 피해자를 돕는 법률 상담 도우미입니다. 간결하고 단계적으로 안내하세요."},
            {"role": "user", "content": user_message},
        ],
        temperature=0.4,
    )
    
    return resp.choices[0].message.content.strip()


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
