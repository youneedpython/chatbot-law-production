"""
core/logger.py

애플리케이션 공통 로깅 설정 모듈. (stdout 기반)

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
"""


import logging
import os
import sys

def get_logger(name: str = 'chatbot-law-prod'):
    logger = logging.getLogger(name)

    level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(level)

    ## 중요! #####################################
    ## 상위(root) 로거로 전파 방지(중복 로그 방지)
    logger.propagate = False
    
    env = (os.getenv('ENV', 'local') or 'local').strip().lower()
    if env in ('prod', 'production'):
        fmt ='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    else:
        fmt = '%(levelname)s | %(name)s | %(message)s'

    ## 이미 핸들러가 있으면, 포맷만 업데이트하고 반환 
    ## reload/재실행 시 핸들러 중복 추가 방지
    if logger.handlers:
        for h in logger.handlers:
            if isinstance(h, logging.StreamHandler):
                h.setFormatter(logging.Formatter(fmt=fmt))
        return logger

    handler = logging.StreamHandler(stream=sys.stdout) ## stdout -> EB/CloudWatch로 수집됨
    handler.setFormatter(logging.Formatter(fmt=fmt))
    logger.addHandler(handler)

    return logger