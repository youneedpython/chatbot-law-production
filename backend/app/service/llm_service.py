import uuid
from functools import lru_cache
from typing import Optional, Any

# from requests import Session
from sqlalchemy.orm import Session  # ✅ 기존 코드의 requests.Session은 오타/부정확 가능성 높음

from app.core.logger import get_logger
from app.core.metrics import now, span
from app.repository.chat import list_messages
from app.service.chain_builder import build_rag_chain

logger = get_logger("chatbot-law-prod.llm")


@lru_cache(maxsize=1)
def get_chain():
    logger.info("Initializing RAG chain (cached).")
    return build_rag_chain()


def ask_llm(db: Session, message: str, session_id: Optional[str] = None):
    """
    Returns:
        (answer: str, session_id: str, sources: list[dict], extra: dict)
    """
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info("Generated new session_id=%s", session_id)

    HISTORY_LIMIT = 20

    # 1. 대화 기록 로드 (최대 HISTORY_LIMIT개)
    t = now()
    history = list_messages(db, session_id, limit=HISTORY_LIMIT)
    ms_history_load = span("db_history_load", t, limit=HISTORY_LIMIT)

    history_text = "\n".join([f"{m.role}: {m.content}" for m in history]).strip()

    if history and history[-1].role == "user" and history[-1].content.strip() == message.strip():
        input_text = f"[대화 기록]\n{history_text}"
    else:
        input_text = (
            f"[대화 기록]\n{history_text}\n\n[사용자 질문]\n{message}"
            if history_text
            else message
        )

    chain = get_chain()

    result = chain({"input": input_text})  # invoke와 동일하게 동작
    answer = (result.get("answer") or "").strip()
    sources = result.get("sources") or []

    logger.info(
        "ask_llm completed. session_id=%s, answer_len=%d, sources=%d",
        session_id,
        len(answer),
        len(sources),
    )

    extra: dict[str, Any] = {"ms_history_load": ms_history_load}
    return answer, session_id, sources, extra
