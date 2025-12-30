"""
models/chat.py

대화 히스토리 저장을 위한 ORM 모델 정의 파일 (v0.4.0 기준).

구성:
- Conversation: 하나의 대화 세션(채팅방)을 나타내는 엔티티
- Message: 대화 내 개별 메시지(user / assistant)

설계 특징:
- Conversation은 session_id(UUID 문자열)를 Primary Key로 사용
- Message는 seq 필드를 통해 대화 내 순서를 명시적으로 보장
- (conversation_id, seq) 유니크 인덱스로 순서 중복 및 경합 방지
- 최신 대화 조회 성능 향상을 위해 updated_at 인덱스 적용
- cascade="all, delete-orphan"으로 대화 삭제 시 메시지 자동 정리

의도:
- LLM 호출(call_llm) 시 이전 대화 컨텍스트를 안정적으로 재구성
- pagination, history 조회, 재질문 시나리오를 고려한 구조
- v0.4.x 이후 RAG, 요약, 재질문 확장에 대응 가능

제약:
- role은 user / assistant 만 허용 (system 메시지는 v0.4.0에서 제외)
"""



from __future__ import annotations

from datetime import datetime
from typing import List, Literal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
    Integer,
    String,
    Text,
    func,
    CheckConstraint,  ## role 제약에 사용
)

from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    ## session_id를 그대로 PK로 사용 (UUID 문자열)
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    ## Postgres 운영에서는 DB가 시간을 책임지게 하는 편이 안정적
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        # default=datetime.utcnow, 
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        # default=datetime.utcnow, 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    ## 최신순 조회/정렬에 유용
    __table_args__ = (
        Index("ix_conversations_updated_at", "updated_at"),
    )

    messages: Mapped[List["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.seq",
        passive_deletes=True,
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
        DateTime(timezone=True), 
        # default=datetime.utcnow, 
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        ## 같은 대화창에서 seq 중복 방지
        # Index("ux_messages_conversation_seq", "conversation_id", "seq", unique=True),
        UniqueConstraint("conversation_id", "seq", name="uq_messages_conversation_seq"),
        ## 조회 성능 향상용 인덱스
        Index("ix_messages_conversation_created_at", "conversation_id", "created_at"),

        ## role 값 DB에서 강제
        # CheckConstraint("role in ("user","assistant")", name="ck_messages_role"),
    )

    conversation: Mapped["Conversation"] = relationship(
        back_populates="messages",
    )
    