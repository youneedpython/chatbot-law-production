"""
########################################################################
logger.py

애플리케이션 전반에서 사용되는 공통 로깅(Logger) 설정 파일입니다.

역할:
- FastAPI backend 전용 로거를 생성하고 설정합니다.
- 로컬 개발 환경과 Production 환경(Docker, AWS)에서
  동일한 방식으로 로그를 수집할 수 있도록 합니다.

특징:
- 로그 중복 출력을 방지하기 위해 handler 중복 생성을 차단합니다.
- 로그는 stdout으로 출력되어 Docker / AWS CloudWatch에서 수집됩니다.
- LOG_LEVEL 환경 변수를 통해 실행 환경별 로그 레벨을 제어할 수 있습니다.

설계 원칙:
- 파일 로그 대신 stdout 기반 로그를 사용합니다.
- logger 설정은 이 파일에서만 수행합니다.
- 비즈니스 로직에서는 get_logger()만 호출합니다.
########################################################################
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