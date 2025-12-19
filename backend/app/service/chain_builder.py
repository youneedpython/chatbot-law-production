"""
service/chain_builder.py

LangChain 기반 LLM 체인(conversational chain)을 생성하는 빌더 모듈 (stateless)

주요 역할
- ChatPromptTemplate + ChatOpenAI + StrOutputParser를 조합해 Runnable 체인을 생성
- keyword_dictionary.json(선택)을 로드해 시스템 프롬프트에 참고 힌트를 제공

중요 설계(현재)
- 이 체인은 히스토리를 내부에 저장하지 않는(stateless) 구조
- 대화 히스토리(컨텍스트)는 service/llm_service.py가 DB에서 조회하여
  입력 텍스트/메시지 형태로 구성해 체인에 전달

호출 예
- chain.stream({"input": "<history + user message>"})
"""


from __future__ import annotations

import json
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import OPENAI_MODEL
from app.core.logger import get_logger


logger = get_logger("chatbot-law-prod.chain_builder")

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
    stateless 대화 체인을 생성해 반환합니다.

    - 이 체인은 히스토리를 내부에 저장하지 않습니다.
    - 입력으로 받은 {"input": "<history + user message>"} 텍스트만을 기반으로 응답을 생성합니다.
    - 대화 히스토리 구성(DB 조회 및 컨텍스트 문자열 조립)은 llm_service.py에서 담당합니다.

    사용 예:
        chain = build_conversational_chain()
        for token in chain.stream({"input": input_text}):
            ...
    """
    keyword_dictionary = load_keyword_dictionary()
    system_prompt = _build_system_prompt(keyword_dictionary)

    ## messages 전체를 통째로 받는 프롬프트로 전환
    ## llm_service에서 DB history를 포함한 messages를 만들어 전달할 것
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0.3)

    # prompt -> llm -> 문자열 파서
    return prompt | llm | StrOutputParser()
