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


from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.metrics import now, span
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
    request: Request,  # ✅ 추가: request.state.metrics에 적재하기 위함
    db: Session = Depends(get_db),
):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="message is empty")

    # ------------------------------------------------------------------
    # 1. user 메시지 저장
    # ------------------------------------------------------------------
    t = now()
    message = payload.message.strip()
    append_message(
        db=db,
        conversation_id=session_id,
        role="user",
        content=message,
    )
    ms_db_user = span("db_append_user", t)
    request.state.metrics["ms_db_user"] = ms_db_user  # ✅ 라우터 단위 메트릭 저장소에 기록

    # ------------------------------------------------------------------
    # 2. LLM 호출 (RAG)
    #    ask_llm은 (answer, session_id, sources, extra)를 반환
    # ------------------------------------------------------------------
    t = now()
    message = payload.message.strip()
    answer, _, sources, extra = ask_llm(
        db=db,
        message=message,
        session_id=session_id,
    )
    ms_ask_llm = span("ask_llm_total", t)
    request.state.metrics["ms_ask_llm"] = ms_ask_llm  # ✅ 라우터 단위 메트릭 저장소에 기록

    # history load도 요청 요약에 포함(2단계 요구)
    if extra and "ms_history_load" in extra:
        request.state.metrics["ms_history_load"] = extra["ms_history_load"]

    # ------------------------------------------------------------------
    # 3. assistant 메시지 저장
    #    ※ DB에는 answer만 저장 (sources는 응답 메타 정보)
    # ------------------------------------------------------------------
    t = now()
    append_message(
        db=db,
        conversation_id=session_id,
        role="assistant",
        content=answer,
    )

    ms_db_assistant = span("db_append_assistant", t)
    request.state.metrics["ms_db_assistant"] = ms_db_assistant  # ✅ 라우터 단위 메트릭 저장소에 기록

    # ------------------------------------------------------------------
    # 4. 응답 반환
    # ------------------------------------------------------------------
    return {
        "session_id": session_id,
        "answer": answer,
        "sources": sources,
    }
