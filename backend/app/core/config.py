"""
core/config.py

애플리케이션 설정(환경 변수)을 단일 진입점에서 로드/검증하는 설정 모듈.

주요 역할
- 로컬(ENV=local)에서는 .env 파일을 로드하고, 운영(prod)에서는 OS 환경변수만 사용
- OpenAI 등 외부 서비스 키/옵션을 환경변수에서 읽어 전역 설정으로 제공
- 필수 환경변수 누락 시 애플리케이션 시작 단계에서 즉시 실패(Fail-Fast)

환경 변수
- ENV: local | prod (기본값: local)
- OPENAI_API_KEY: (필수) OpenAI API Key
- OPENAI_MODEL: (선택) 기본값 gpt-4o-mini
- PINECONE_API_KEY: (선택)
- LANGCHAIN_TRACING_V2: (선택) true/false 문자열 → bool
- LANGSMITH_API_KEY: (선택)

주의
- 비밀키 하드코딩 금지. 모든 설정은 이 모듈을 통해서만 접근.
"""


import os
from dotenv import load_dotenv


# ======================================
# Environment configuration
# ======================================
# 로컬 개발: .env가 존재하면 로드 (prod/eb에서는 보통 .env 없음)
load_dotenv()

ENV = os.getenv('ENV', 'local')


# ======================================
# Required settings
# ======================================
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def validate_runtime_env():
    """
    애플리케이션 런타임에서만 필요한 환경변수 검증
    (Alembic / CI 단계에서는 호출하지 않음)
    """
    if not OPENAI_API_KEY:
        raise RuntimeError('OPENAI_API_KEY environment variable is required.')

OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')

# ======================================
# Optional / future settings
# ======================================
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
LANGSMITH_API_KEY = os.getenv('LANGSMITH_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'chatbot-law-dev')
PINECONE_TOP_K = int(os.getenv("PINECONE_TOP_K", "5"))  # 검색된 문서 개수


# ======================================
# Database settings
# ======================================
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")