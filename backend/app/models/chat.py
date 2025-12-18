"""
models/chat.py
- v0.4.0 대화 히스토리용 모델
  - Conversation: session_id 단위 대화방
  - Message: user/assistant 메시지 (seq로 정렬 안정화)
"""


from __future__ import annotations

from datetime import datetime
from typing import List, Literal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class Conversation(Base):
    __tablename__ = "conversations"

    ## session_id를 그대로 PK로 사용 (UUID 문자열)
    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    ## 최신순 조회/정렬에 유용
    __table_args__ = (
        Index('ix_conversations_updated_at', 'updated_at'),
    )

    messages: Mapped[List["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.seq",
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    conversation_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    ## user / assistant 만 사용 (system은 v0.4.0에서 제외)
    role: Mapped[Literal["user", "assistant"]] = mapped_column(String(16), nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)

    ## 대화 내 순서 보장용 (pagination 시 안정적 정렬에 필요)
    seq: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        ## 같은 대화창에서 seq 중복 방지
        Index("ux_messages_conversation_seq", "conversation_id", "seq", unique=True),
        ## 조회 성능 향상용 인덱스
        Index("ix_messages_conversation_created_at", "conversation_id", "created_at"),
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")



    