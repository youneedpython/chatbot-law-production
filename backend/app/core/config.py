"""
########################################################################
config.py

애플리케이션 전반에서 사용되는 환경 변수(Environment Variables)를
중앙에서 관리하는 설정 파일입니다.

역할:
- OpenAI, Pinecone, LangChain 등 외부 서비스 관련 환경 변수를 로드합니다.
- 로컬 개발 환경에서는 .env 파일을 사용하고,
  Production 환경(AWS, Docker 등)에서는 OS 환경 변수를 사용합니다.

설계 원칙:
- 모든 설정 값은 이 파일을 통해서만 접근합니다.
- 하드코딩된 비밀 키(API Key)는 절대 포함하지 않습니다.
- 필수 환경 변수는 애플리케이션 시작 시 검증하여 조기 실패(Fail Fast)합니다.

환경 구분:
- ENV=local  → .env 파일 로드 (기본값)
- ENV=prod   → OS 환경 변수만 사용
########################################################################
"""

import os
from dotenv import load_dotenv


# ======================================
# Environment configuration
# ======================================
# 로컬 개발 환경에서만 .env 로드
if os.getenv('ENV', 'local') == 'local':
    load_dotenv()


# ======================================
# Required settings
# ======================================
OPENAPI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAPI_API_KEY:
    raise RuntimeError('OPENAI_API_KEY environment variable is required.')

OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

# ======================================
# Optional / future settings
# ======================================
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
LANGSMITH_API_KEY = os.getenv('LANGSMITH_API_KEY')