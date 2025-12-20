"""
service/llm_service.py

LLM 호출을 담당하는 Service 계층 모듈 (DB 기반 히스토리).

주요 역할
- session_id와 사용자 메시지를 받아 LLM 응답을 생성해 반환
- 대화 히스토리는 DB(repository.list_messages)에서 조회하여 컨텍스트로 사용
- 체인 객체는 lru_cache로 캐싱하여 재사용

원칙
- 히스토리 저장/조회 진실의 원천은 DB
- 라우터는 이 모듈의 ask_llm()만 호출
"""


import uuid
from functools import lru_cache
from typing import Optional, Literal, TypedDict

from requests import Session

from app.core.logger import get_logger
from app.service.chain_builder import build_conversational_chain
from app.repository.chat import list_messages


logger = get_logger('chatbot-law-prod.llm')

Role = Literal['user', 'assistant']

class Message(TypedDict):
    role: Role
    content: str

## v0.3.0: 메모리 저장소 (서버 재시작하면 날아감)
# SESSION_STORE: Dict[str, List[Message]] = {}


@lru_cache(maxsize=1) ## 함수 반환값을 캐싱하여 재사용
def get_chain():
    """
    대화 체인 1개 생성하여 캐싱 후 반환
    이후 모든 요청에서는 캐싱된 체인을 재사용
    - 체인은 stateless로 유지되며 히스토리는 DB에서 조회하여 입력 컨텍스트로 구성
    - session_id는 DB에서 어떤 대화방을 조회할지 결정하는 키로 사용됨

    1) 비용 절감: 매 요청마다 체인/모델 객체를 새로 생성하지 않음
    2) 성능 향상: 체인/모델 초기화 오버헤드를 줄임

    Returns:    
        build_conversational_chain()의 반환값 (대화 체인 객체) 

    cf) 
    lru_cache 문서: https://docs.python.org/3/library/functools.html#functools.lru_cache
    LRU: Least Recently Used (가장 최근에 사용된 항목을 우선 캐싱)
    """
    logger.info('Initializing conversational chain (cached).')
    return build_conversational_chain()


def ask_llm(db: Session, message: str, session_id: Optional[str] = None) -> tuple[str, str]:
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
    HISTORY_LIMIT = 20
    history = list_messages(db, session_id, limit=HISTORY_LIMIT)

    ## DB history를 텍스트 컨텍스트로 구성
    ## (나중에 MessagesPlaceholder로 확장 가능)
    history_text = '\n'.join([f'{m.role}: {m.content}' for m in history]).strip()

    ## user message는 router가 이미 DB에 저장했으니
    ## history에 포함되어 있을 수 있음 -> 중복 방지
    ## 가장 간단한 방지: 마지막이 user이고 내용이 동일하면 다시 붙이지 않기
    if history and history[-1].role == "user" and history[-1].content.strip() == message.strip():
        # history_text에 이미 포함된 것으로 보고 message를 별도 섹션에만 표시하거나,
        # 또는 message를 생략하는 정책으로 조정
        input_text = f"[대화 기록]\n{history_text}"
    else:
        input_text = f"[대화 기록]\n{history_text}\n\n[사용자 질문]\n{message}" if history_text else message

    ## 2) LLM 호출 (기존 체인 방식 유지)
    chain = get_chain()
    logger.info('chain : %s', chain)

    ## MVP: stream 토큰을 모두 모아 최종 문자열로 반환
    chunks = []
    for token in chain.stream({'input': input_text}):
        ## token은 str 또는 특별 토큰 객체일 수 있음
        ## token이 문자열이 아닐 가능성에 대비 (안전장치)
        chunks.append(token if isinstance(token, str) else str(token))
    
    # logger.info('chunks: %s', chunks)

    answer = ''.join(chunks).strip()
    logger.info('ask_llm completed. session_id=%s, answer_len=%d', session_id, len(answer))

    return answer, session_id