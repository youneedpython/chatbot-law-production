from functools import lru_cache

from langchain_pinecone import PineconeVectorStore

from app.core.config import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    RAG_TOP_K,
)
from app.core.logger import get_logger
from app.service.embeddings_service import get_embeddings

logger = get_logger("chatbot-law-prod.retriever")


@lru_cache(maxsize=1)
def get_retriever():
    """
    Pinecone 기반 Retriever를 생성하여 캐싱 후 반환합니다.

    - VectorDB는 외부 상태를 가지므로, 매 요청마다 재생성할 필요 없음
    - top_k 등 검색 파라미터는 config에서 관리
    """
    logger.info(
        "Initializing Pinecone retriever (cached). index=%s, top_k=%s",
        PINECONE_INDEX_NAME,
        RAG_TOP_K,
    )

    embeddings = get_embeddings()

    vectorstore = PineconeVectorStore(
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings,
        pinecone_api_key=PINECONE_API_KEY,
    )

    return vectorstore.as_retriever(
        search_kwargs={
            "k": RAG_TOP_K,
        }
    )
