from functools import lru_cache

from langchain_openai import OpenAIEmbeddings

from app.core.config import OPENAI_EMBEDDING_MODEL
from app.core.logger import get_logger

logger = get_logger("chatbot-law-prod.embeddings")


@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
    """
    OpenAI Embeddings 객체를 생성하여 캐싱 후 반환합니다.

    - indexing 파이프라인과 동일한 모델을 사용해야 함
    - 서비스 전반에서 단일 embeddings 인스턴스를 공유
    """
    logger.info(
        "Initializing OpenAIEmbeddings (cached). model=%s",
        OPENAI_EMBEDDING_MODEL,
    )
    return OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)
