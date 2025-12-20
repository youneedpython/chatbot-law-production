"""
repository/chat.py
- v0.4.0 대화 히스토리 CRUD (Conversation / Message)
- 핵심 기능:
  - get_or_create_conversation(session_id)
  - append_message(conversation_id, role, content) -> seq 자동 증가
  - list_messages(conversation_id, limit, before_seq)
"""


from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional, List

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.chat import Conversation, Message


Role = Literal["user", "assistant"]

def get_or_create_conversation(db: Session, session_id:str) -> Conversation:
    """
    session_id(=Conversation.id)로 대화창을 조회하고, 없으면 생성한다.
    """
    convo = db.get(Conversation, session_id)

    if convo:
        return convo
    
    convo = Conversation(
        id=session_id, 
        created_at=datetime.utcnow(), 
        updated_at=datetime.utcnow(),
    )

    db.add(convo)
    db.commit()
    db.refresh(convo)

    return convo


def _next_seq(db: Session, conversation_id: str) -> int:
    """
    해당 conversation의 다음 seq 값을 계산한다.
    (messages 테이블에서 max(seq) + 1)
    """

    max_seq_stmt = select(func.max(Message.seq)).where(Message.conversation_id == conversation_id)
    max_seq = db.execute(max_seq_stmt).scalar_one_or_none()

    return (max_seq or 0) + 1

def append_message(
        db: Session,
        conversation_id: str,
        role: Role,
        content: str,
    ) -> Message:
    """
    메시지를 DB에 append한다.
    - seq는 자동 증가
    - conversation.updated_at 갱신
    """
    convo = get_or_create_conversation(db, conversation_id)

    seq = _next_seq(db, conversation_id)
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        seq=seq,
        created_at=datetime.utcnow()
    )
    db.add(msg)

    convo.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(msg)

    return msg


def list_messages(
        db: Session,
        conversation_id: str,
        limit: int = 50,
        before_seq: Optional[int] = None,
) -> List[Message]:
    """
    대화 히스토리 조회
    - 기본: seq 오름차순으로 최근 limit개 반환
    - before_seq가 있으면: 해당 seq 이전 메시지들 중 최근 limit개
    """
    ## 존재 확인(없으면 빈 리스트)
    convo = db.get(Conversation, conversation_id)

    if not convo:
        return []

    stmt = select(Message).where(Message.conversation_id == conversation_id)

    if before_seq is not None:
        stmt = stmt.where(Message.seq < before_seq)

    ## 최신 limit개를 뽑아 정렬을 안정적으로 하기 위해:
    ## 1) seq 내림차순으로 limit
    ## 2) 결과를 다시 오름차순으로 정렬해서 반환
    stmt = stmt.order_by(Message.seq.desc()).limit(limit)

    items = db.execute(stmt).scalars().all()
    items.sort(key=lambda m: m.seq)

    return items