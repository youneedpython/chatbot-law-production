"""
core/logger.py

애플리케이션 공통 로깅 설정 모듈 (stdout 기반)

주요 역할
- 실행 환경(local/prod)에 맞는 포맷으로 Logger를 생성/반환
- handler 중복 생성을 방지하여 reload/다중 import에서도 로그 중복 출력 방지
- stdout(StreamHandler)로 출력하여 Docker/AWS(CloudWatch 등)에서 수집 가능

환경 변수
- LOG_LEVEL: DEBUG | INFO | WARNING | ERROR | CRITICAL (기본값: INFO)
- ENV: local | prod/production (prod일 때 timestamp 포함 포맷 사용)

사용 원칙
- 비즈니스 로직에서는 logging 설정을 직접 하지 말고 get_logger()만 호출
- root 로거 전파(propagate)는 False로 유지하여 중복 로그를 방지

추가 사항 (v0.4.2)
- RequestIdFilter를 통해 요청 단위 request_id를 LogRecord에 자동 주입
- 포맷에 request_id 포함
"""


import logging
import os
import sys


class RequestIdFilter(logging.Filter):
    """ContextVar에 저장된 request_id를 LogRecord에 주입"""
    def filter(self, record: logging.LogRecord) -> bool:
        ## 순환 import를 피하려고 함수 내부 import
        from app.core.request_id import get_request_id
        record.request_id = get_request_id() or "-"
        return True


def _ensure_request_id_filter(handler: logging.Handler) -> None:
    """handler에 RequestIdFilter가 없으면 추가한다(중복 방지)"""
    for f in handler.filters:
        if isinstance(f, RequestIdFilter):
            return
    handler.addFilter(RequestIdFilter())


def get_logger(name: str = 'chatbot-law-prod') -> logging.Logger:
    logger = logging.getLogger(name)

    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    ## 중요! #####################################
    ## 상위(root) 로거로 전파 방지(중복 로그 방지)
    logger.propagate = False
    
    env = (os.getenv('ENV', 'local') or 'local').strip().lower()
    if env in ('prod', 'production'):
        fmt ='%(asctime)s | %(levelname)s | %(name)s | %(request_id)s | %(message)s'
    else:
        fmt = '%(levelname)s | %(name)s | %(request_id)s | %(message)s'

    ## 이미 핸들러가 있으면, 포맷 업데이트 + 필터 주입 후 반환
    ## reload/재실행 시 핸들러 중복 추가 방지
    if logger.handlers:
        for h in logger.handlers:
            if isinstance(h, logging.StreamHandler):
                _ensure_request_id_filter(h)
                h.setFormatter(logging.Formatter(fmt=fmt))
        return logger

    handler = logging.StreamHandler(stream=sys.stdout) ## stdout -> EB/CloudWatch로 수집됨
    _ensure_request_id_filter(handler)
    handler.setFormatter(logging.Formatter(fmt=fmt))
    logger.addHandler(handler)

    return logger