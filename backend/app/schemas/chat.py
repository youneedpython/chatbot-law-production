"""
schemas/chat.py

대화 히스토리(Conversation / Message) API에서 사용하는 Pydantic 스키마 정의 파일.

사용 범위
- routers/history.py 에서 요청/응답 모델로 사용
- SQLAlchemy Message 모델을 API 응답 형태로 직렬화

구성
- MessageCreate: 메시지 생성 요청용 스키마
- MessageResponse: 단일 메시지 응답 스키마
- MessageListResponse: 메시지 목록 + pagination 정보

설계 원칙
- role은 user / assistant 만 허용하여 도메인 일관성 유지
- from_attributes=True 설정으로 ORM 객체를 직접 응답 모델로 변환
- API 계층과 DB 계층 간 명확한 분리 유지
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

