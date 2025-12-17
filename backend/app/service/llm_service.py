"""
########################################################################
llm_service.py

LLM(대화형 체인) 호출을 담당하는 서비스(Service) 계층 파일입니다.

역할:
- API 라우터(routes_chat.py)에서 받은 사용자 메시지를 LLM 체인에 전달합니다.
- 세션 식별자(session_id)를 관리하여 대화 컨텍스트(히스토리/메모리)를 유지할 수 있게 합니다.
- 체인 객체는 비용/성능을 위해 캐싱(lru_cache)하여 재사용합니다.

동작 개요:
1) session_id가 없으면 새로 생성(uuid4)
2) get_chain()으로 체인 객체를 가져오거나 생성(캐시)
3) chain.stream(...) 결과 토큰들을 모아 최종 답변 문자열로 반환

주의사항:
- 이 파일은 "비즈니스 로직"만 담당하며, HTTP 요청/응답 처리는 routes에서 수행합니다.
- 운영 로그에는 개인정보/민감정보(사용자 질문 원문, 키 등)를 남기지 않도록 주의합니다.
########################################################################
"""

import uuid
from functools import lru_cache
from typing import Optional, Dict, List, Literal, TypedDict

from app.core.logger import get_logger
from app.service.chain_builder import build_conversational_chain


logger = get_logger('chatbot-law-prod.llm')

Role = Literal['user', 'assistant']

class Message(TypedDict):
    role: Role
    content: str

## v0.3.0: 메모리 저장소 (서버 재시작하면 날아감)
SESSION_STORE: Dict[str, List[Message]] = {}


@lru_cache(maxsize=1) ## 함수 반환값을 캐싱하여 재사용
def get_chain():
    """
    대화 체인 1개 생성하여 캐싱 후 반환합니다.
    이후 모든 요청에서는 캐싱된 체인을 재사용합니다.
    세션별 대화는 session_id로 구분된 히스토리로 관리됩니다.

    1) 비용 절감: 매 요청마다 체인/모델 객체를 새로 생성하지 않음
    2) 성능 향상: 체인/모델 초기화 오버헤드를 줄임
    3) 주의: 체인 내부 상태(히스토리 등)는 session_id로 구분 관리됨

    Returns:    
        build_conversational_chain()의 반환값 (대화 체인 객체) 

    cf) 
    lru_cache 문서: https://docs.python.org/3/library/functools.html#functools.lru_cache
    LRU: Least Recently Used (가장 최근에 사용된 항목을 우선 캐싱)
    """
    logger.info('Initializing conversational chain (cached).')
    return build_conversational_chain()


def append_history(session_id: str, role: Role, content: str) -> None:
    """
    세션별 대화 히스토리에 메시지를 추가합니다.

    Args:
        session_id (str): 대화 세션 식별자
        role (Role): 메시지 역할 ('user' 또는 'assistant')
        content (str): 메시지 내용
    """
    SESSION_STORE.setdefault(session_id, []).append({'role': role, 'content': content})


def get_history(session_id: str) -> List[Message]:
    """
    세션별 대화 히스토리를 반환합니다.

    Args:
        session_id (str): 대화 세션 식별자

    Returns:
        List[Message]: 해당 세션의 대화 히스토리 메시지 목록
    """
    return SESSION_STORE.get(session_id, [])


def ask_llm(message: str, session_id: Optional[str] = None):
    """
    LLM에게 질문을 전달하고 답변과 session_id를 반환합니다.

    Args:
        message (str): 사용자 질문 메시지
        session_id (str | None): 대화 세션 식별자 (없으면 새로 생성)

    Returns:
        Tuple[str, str]: LLM 답변 문자열과 session_id
    """
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info("Generated new session_id=%s", session_id)

    logger.info("ask_llm called. session_id=%s, msg_len=%d", session_id, len(message))

    ## 1) user 메시지 히스토리에 추가
    append_history(session_id, 'user', message)

    ## 2) LLM 호출 (기존 체인 방식 유지)
    chain = get_chain()
    logger.info('chain : %s', chain)

    ## MVP: stream 토큰을 모두 모아 최종 문자열로 반환
    chunks = []
    for token in chain.stream(
        {'input': message},
        config={'configurable': {'session_id': session_id}},
    ):
        ## token은 str 또는 특별 토큰 객체일 수 있음
        ## token이 문자열이 아닐 가능성에 대비 (안전장치)
        chunks.append(token if isinstance(token, str) else str(token))
    
    # logger.info('chunks: %s', chunks)

    answer = ''.join(chunks).strip()
    logger.info('ask_llm completed. session_id=%s, answer_len=%d', session_id, len(answer))

    ## 3) assistant 메시지 히스토리에 추가
    append_history(session_id, 'assistant', answer)

    logger.info("chat completed | session_id=%s | user_len=%s | answer_len=%s",
                session_id, len(message), len(answer))

    return answer, session_id

