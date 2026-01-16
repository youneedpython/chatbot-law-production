from __future__ import annotations

import json
from pathlib import Path
from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import OPENAI_MODEL
from app.core.logger import get_logger
from app.service.retriever_service import get_retriever

logger = get_logger("chatbot-law-prod.chain_builder")


# -----------------------------------------------------------------------------
# Keyword dictionary (optional)
# -----------------------------------------------------------------------------
def load_keyword_dictionary() -> dict:
    data_path = Path(__file__).resolve().parents[1] / "data" / "keyword_dictionary.json"

    if not data_path.exists():
        logger.warning("keyword_dictionary.json not found: %s", data_path)
        return {}

    try:
        with data_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.exception("Failed to load keyword_dictionary.json: %s", e)
        return {}


def _build_system_prompt(keyword_dictionary: dict) -> str:
    base = (
        "당신은 '전세사기피해 상담 챗봇'입니다.\n"
        "한국의 전세사기 피해, 예방, 신고, 법적 절차에 대해 설명합니다.\n"
        "단정적인 법률 판단은 피하고, 가능한 절차·기관·준비서류 중심으로 안내하십시오.\n"
        "답변은 번호 목록 형태로 명확하게 작성하십시오.\n"
        "아래 제공된 '참고 문서 내용'을 우선적으로 활용해 답변하십시오.\n"
    )

    if keyword_dictionary:
        keys_preview = ", ".join(list(keyword_dictionary.keys())[:20])
        base += f"\n참고 키워드(일부): {keys_preview}\n"

    return base


def _format_docs(docs: List[Document]) -> str:
    """
    검색된 문서들을 LLM 프롬프트용 컨텍스트 문자열로 변환
    """
    chunks = []
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "unknown")
        chunk_id = doc.metadata.get("chunk_id", "")
        chunks.append(
            f"[문서 {i}]\n"
            f"출처: {source} {chunk_id}\n"
            f"{doc.page_content}"
        )
    return "\n\n".join(chunks)


# -----------------------------------------------------------------------------
# RAG Chain Builder (stateless)
# -----------------------------------------------------------------------------
def build_rag_chain():
    """
    Pinecone Retrieval + LLM Answer 체인을 생성합니다.

    - 체인은 stateless
    - 히스토리는 외부(llm_service)에서 문자열로 구성하여 전달
    - input:
        {
          "input": "<history + user question>"
        }
    """
    keyword_dictionary = load_keyword_dictionary()
    system_prompt = _build_system_prompt(keyword_dictionary)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            (
                "human",
                "아래는 참고 문서 내용입니다.\n"
                "{context}\n\n"
                "아래는 대화 기록 및 사용자 질문입니다.\n"
                "{input}",
            ),
        ]
    )

    llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0.3)
    retriever = get_retriever()

    def _rag_invoke(inputs: dict) -> dict:
        query = inputs["input"]
        docs = retriever.invoke(query)

        logger.info("Retrieved %d documents from Pinecone", len(docs))

        context = _format_docs(docs)
        return {
            "input": query,
            "context": context,
            "source_documents": docs,
        }

    # Runnable composition
    return (
        _rag_invoke
        | prompt
        | llm
        | StrOutputParser()
    )
