"""
schemas/chat.py
- v0.4.0 대화 히스토리 API용 Pydantic 스키마
"""

from datetime import datetime
from typing import Literal, List, Optional

from pydantic import BaseModel, Field


Role = Literal["user", "assistant"]

class MessageCreate(BaseModel):
    role: Role = Field(..., description="메시지 작성 주체 (user | assistant)")
    content: str = Field(..., description="메시지 내용")


class MessageResponse(BaseModel):
    id: int
    role: Role
    content: str
    seq: int
    created_at: datetime

    class Config:
        from_attributes = True  ## SQLAlchemy 모델 -> Pydantic 변환 허용


class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    has_more: bool

