from __future__ import annotations

import json
from pathlib import Path
from typing import List, Any, Dict, Tuple

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
        "답변은 번호 목록 형태를 선호합니다.\n\n"
        "중요: 아래 제공된 [참고 문서]에 근거하여 답변하십시오.\n"
        "각 문단(또는 문장) 끝에는 반드시 근거 문서 번호를 [1], [2] 형태로 표기하십시오.\n"
        "근거가 부족하면 '자료 근거가 부족함'을 명시하고 일반 안내로 전환하십시오.\n"
        "절대 존재하지 않는 출처 번호를 만들지 마십시오.\n"
    )

    if keyword_dictionary:
        keys_preview = ", ".join(list(keyword_dictionary.keys())[:20])
        base += f"\n참고 키워드(일부): {keys_preview}\n"
    return base


def _format_docs_with_citation_numbers(docs: List[Document]) -> Tuple[str, List[Dict[str, Any]]]:
    """
    - LLM에 넣을 context: [1] ... [2] ... 형태로 번호 부여
    - API로 내려줄 sources 배열 생성
    """
    context_blocks: List[str] = []
    sources: List[Dict[str, Any]] = []

    for idx, doc in enumerate(docs, start=1):
        meta = doc.metadata or {}
        source = meta.get("source") or meta.get("doc_id") or "unknown"
        chunk_id = meta.get("chunk_id") or meta.get("chunk") or ""
        page = meta.get("page")

        # LLM context (번호 + 출처 메타 + 본문)
        header = f"[{idx}] 출처: {source}"
        if page is not None:
            header += f" (p.{page})"
        if chunk_id:
            header += f" / chunk: {chunk_id}"

        context_blocks.append(f"{header}\n{doc.page_content}")

        # API sources (LLM이 아닌 시스템이 생성)
        sources.append(
            {
                "id": idx,
                "source": source,
                "page": page,
                "chunk_id": chunk_id,
            }
        )

    context_text = "\n\n---\n\n".join(context_blocks).strip()
    return context_text, sources


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
    - 반환값: Runnable
    - invoke({"input": "..."} ) -> {"answer": str, "sources": list}    
    """
    keyword_dictionary = load_keyword_dictionary()
    system_prompt = _build_system_prompt(keyword_dictionary)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            (
                "human",
                "아래는 참고 문서입니다.\n"
                "{context}\n\n"
                "아래는 대화 기록 및 사용자 질문입니다.\n"
                "{input}\n\n"
                "작성 규칙:\n"
                "1) 답변은 번호 목록으로 구성\n"
                "2) 각 문단(또는 문장) 끝에 반드시 [1], [2] 형태로 근거 표기\n"
                "3) 근거가 없는 내용은 억지로 인용하지 말고 '근거 부족'이라고 명시\n",
            ),
        ]
    )

    llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0.3)
    retriever = get_retriever()
    parser = StrOutputParser()

    def _invoke(inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs["input"]

        # 1) Retrieve
        docs = retriever.invoke(query)
        logger.info("Retrieved %d documents from Pinecone", len(docs))

        # 2) Build context + sources
        context, sources = _format_docs_with_citation_numbers(docs)

        # 3) LLM answer with forced citation format
        msg = prompt.invoke({"input": query, "context": context})
        answer = parser.invoke(llm.invoke(msg)).strip()

        return {"answer": answer, "sources": sources}

    return _invoke
