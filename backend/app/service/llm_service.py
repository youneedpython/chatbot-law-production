import hashlib
import uuid
from functools import lru_cache
from typing import Optional, Any

# from requests import Session
from sqlalchemy.orm import Session

from app.core.config import (
    OPENAI_MODEL,
    LLM_PROVIDER_MODE,
    LLM_AB_RATIO,
    BEDROCK_MODEL_ID,
    )
from app.core.logger import get_logger
from app.core.metrics import now, span
from app.repository.chat import list_messages
from app.service.chain_builder import build_rag_chain

logger = get_logger("chatbot-law-prod.llm")


def select_provider(session_id: str) -> str:
    """
    provider 선택:
    - openai: OpenAI만 사용
    - bedrock: Bedrock만 사용
    - ab: session_id 해시 기반 50:50(or ration) 분기
    """
    mode = LLM_PROVIDER_MODE

    if mode in ("openai", "bedrock"):
        return mode
    
    if mode == "ab":
        digest = hashlib.md5(session_id.encode("utf-8")).hexdigest()
        bucket = int(digest, 16) % 100
        return "openai" if bucket < LLM_AB_RATIO else "bedrock"
    
    ## fallback
    return "openai"


def get_model_name(provider: str) -> str:
    if provider == "bedrock":
        return BEDROCK_MODEL_ID
    return OPENAI_MODEL

@lru_cache(maxsize=8)
def get_chain(provider: str, model_name: str):
    logger.info(
        "Initializing RAG chain (cached). provider=%s, model=%s",
        provider,
        model_name,
    )
    return build_rag_chain(provider=provider, model_name=model_name)


def ask_llm(db: Session, message: str, session_id: Optional[str] = None):
    """
    Returns:
        (answer: str, session_id: str, sources: list[dict], extra: dict)
    """
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info("Generated new session_id=%s", session_id)

    provider = select_provider(session_id)
    model_name = get_model_name(provider)

    HISTORY_LIMIT = 20

    ## 1. 대화 기록 로드 (최대 HISTORY_LIMIT개)
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

    chain = get_chain(provider, model_name)
    result = chain({"input": input_text})  # invoke와 동일하게 동작

    answer = (result.get("answer") or "").strip()
    sources = result.get("sources") or []

    logger.info(
        "ask_llm completed. session_id=%s, model=%s, model_name=%s, answer_len=%d, sources=%d",
        session_id,
        provider,
        model_name,
        len(answer),
        len(sources),
    )

    ## A/B를 위한 최소 메타
    extra: dict[str, Any] = {
        "ms_history_load": ms_history_load,
        "provider": provider,
        "model": model_name,
    }

    return answer, session_id, sources, extra
