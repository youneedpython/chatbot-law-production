"""
core/request_id.py

FastAPI 요청 단위 request_id 생성/보관/조회하는 유틸

- 요청 헤더 X-Request-ID가 있으면 그 값을 사용
- 없으면 UUID4로 생성
- ContextVar에 저장하여(요청 단위) 어디서든 request_id를 꺼내 쓸 수 있게 함
"""


from __future__ import annotations

import uuid
from contextvars import ContextVar
from typing import Optional


REQUEST_ID_HEADER = "X-Request-ID"

_request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def set_request_id(value: Optional[str]) -> None:
    _request_id_ctx.set(value)

def get_request_id() -> Optional[str]:
    return _request_id_ctx.get()

def generate_request_id() -> str:
    return str(uuid.uuid4())