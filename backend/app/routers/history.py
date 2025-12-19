"""
routers/history.py
- v0.4.0 대화 히스토리 API
  - GET  /api/conversations/{session_id}/messages
  - POST /api/conversations/{session_id}/messages
"""


from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.repository.chat import (
    append_message,
    list_messages,
)
from app.schemas.chat import (
    MessageCreate,
    MessageListResponse,
    MessageResponse
)


router = APIRouter(
    prefix="/conversations",
    tags=["History"],
)

@router.get("/{session_id}/messages", response_model=MessageListResponse,)
def get_messages(
    session_id: str,
    limit: int = Query(50, ge=1, le=100),
    before_seq: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db),
):
    """
    특정 대화방(session_id)의 메시지 히스토리 조회
    """
    items = list_messages(
        db=db,
        conversation_id=session_id,
        limit=limit,
        before_seq=before_seq,
    )

    has_more = len(items) == limit

    return MessageListResponse(
        messages=items,
        has_more=has_more,
    )


@router.post("/{session_id}/messages", response_model=MessageResponse,)
def post_message(
    session_id: str,
    payload: MessageCreate,
    db: Session = Depends(get_db),
):
    """
    특정 대화방(session_id)에 메시지 저장
    (user / assistant 공용)
    """   
    msg = append_message(
        db=db,
        conversation_id=session_id,
        role=payload.role,
        content=payload.content,
    )

    return msg
