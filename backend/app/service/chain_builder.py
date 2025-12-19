"""
service/chain_builder.py

LangChain 기반의 대화형 LLM 체인(conversational chain)을 구성/생성하는 빌더 모듈

주요 역할
- ChatPromptTemplate + ChatOpenAI + OutputParser(StrOutputParser)를 조합해 Runnable 체인을 생성
- RunnableWithMessageHistory를 적용하여 session_id 기반 대화 히스토리를 유지
- keyword_dictionary.json(선택)을 로드해 시스템 프롬프트에 참고 힌트를 제공

히스토리 저장 방식 (현재)
- in-memory dict(_SESSION_STORE) + ChatMessageHistory 사용 (MVP)
- 서버 재시작/스케일아웃 시 히스토리 유실 가능
  → 프로덕션에서는 DB/Redis 등 영속 저장소 연동 권장

사용 예
- llm_service.py에서 build_conversational_chain()로 체인을 받은 뒤
  chain.stream({"input": message}, config={"configurable": {"session_id": session_id}})
  형태로 호출
"""


from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

from app.core.config import OPENAI_MODEL
from app.core.logger import get_logger


logger = get_logger("chatbot-law-prod.chain_builder")

# -----------------------------------------------------------------------------
# In-memory session store (MVP)
# -----------------------------------------------------------------------------
_SESSION_STORE: Dict[str, ChatMessageHistory] = {}


def _get_history(session_id: str) -> ChatMessageHistory:
    """session_id 별 대화 히스토리 객체를 반환합니다 (메모리 저장)."""
    if session_id not in _SESSION_STORE:
        _SESSION_STORE[session_id] = ChatMessageHistory()
    return _SESSION_STORE[session_id]


# -----------------------------------------------------------------------------
# Keyword dictionary (optional)
# -----------------------------------------------------------------------------
def load_keyword_dictionary() -> dict:
    """
    keyword_dictionary.json을 로드합니다.

    파일 위치:
    backend/app/data/keyword_dictionary.json
    """
    # chain_builder.py는 backend/app/service/에 있으므로 parents[1] == backend/app
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
    """
    시스템 프롬프트를 구성합니다.
    - MVP에서는 dictionary를 '참고 정보'로만 사용합니다.
    - 추후: 키워드별 답변 템플릿/가이드/법 조항 인용 정책으로 확장 가능
    """
    base = (
        "당신은 '전세사기피해 상담 챗봇'입니다.\n"
        "사용자가 전세사기 피해/예방/신고/법적 절차 등을 질문하면, 한국 상황을 기준으로\n"
        "정확하고 단계적으로 안내하되, 단정적인 법률 판단은 피하고 '가능한 절차/기관/준비서류' 중심으로 설명하라.\n"
        "답변은 읽기 쉬운 번호 목록 형태를 선호한다.\n"
    )

    # dictionary가 있으면 키 목록 정도만 힌트로 제공 (너무 길면 토큰 낭비)
    if keyword_dictionary:
        keys_preview = ", ".join(list(keyword_dictionary.keys())[:20])
        base += f"\n참고 키워드(일부): {keys_preview}\n"

    return base


# -----------------------------------------------------------------------------
# Chain builder
# -----------------------------------------------------------------------------
def build_conversational_chain():
    """
    대화형 체인을 생성하여 반환합니다.

    반환되는 객체는:
    - .invoke() / .stream() 등을 사용할 수 있고,
    - RunnableWithMessageHistory로 감싸져 있어 session_id 기반 히스토리를 유지합니다.

    llm_service.py에서:
    chain.stream({"input": message}, config={"configurable": {"session_id": session_id}})
    형태로 호출하면 됩니다.
    """
    keyword_dictionary = load_keyword_dictionary()
    system_prompt = _build_system_prompt(keyword_dictionary)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    llm = ChatOpenAI(model=OPENAI_MODEL)

    # prompt -> llm -> 문자열 파서
    core_chain = prompt | llm | StrOutputParser()

    # session_id 기반 history 연결
    chain_with_history = RunnableWithMessageHistory(
        core_chain,
        _get_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    return chain_with_history
