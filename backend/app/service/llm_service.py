import uuid
from functools import lru_cache
from typing import Optional

from requests import Session

from app.core.logger import get_logger
from app.repository.chat import list_messages
from app.service.chain_builder import build_rag_chain

logger = get_logger("chatbot-law-prod.llm")


@lru_cache(maxsize=1)
def get_chain():
    logger.info("Initializing RAG chain (cached).")
    return build_rag_chain()


def ask_llm(db: Session, message: str, session_id: Optional[str] = None) -> tuple[str, str]:
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info("Generated new session_id=%s", session_id)

    HISTORY_LIMIT = 20
    history = list_messages(db, session_id, limit=HISTORY_LIMIT)

    history_text = "\n".join(
        [f"{m.role}: {m.content}" for m in history]
    ).strip()

    if history and history[-1].role == "user" and history[-1].content.strip() == message.strip():
        input_text = f"[대화 기록]\n{history_text}"
    else:
        input_text = (
            f"[대화 기록]\n{history_text}\n\n[사용자 질문]\n{message}"
            if history_text
            else message
        )

    chain = get_chain()

    chunks = []
    for token in chain.stream({"input": input_text}):
        chunks.append(token if isinstance(token, str) else str(token))

    answer = "".join(chunks).strip()

    logger.info(
        "ask_llm completed. session_id=%s, answer_len=%d",
        session_id,
        len(answer),
    )

    return answer, session_id
