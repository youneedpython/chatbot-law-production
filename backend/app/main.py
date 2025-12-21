"""
app/main.py

FastAPI 애플리케이션 엔트리 포인트

역할
- FastAPI 앱 객체 생성
- 라우터(chat, history, health) 등록 및 API prefix 구성
  - /api/chat/...
  - /api/conversations/...
  - /health

운영 참고
- 배포 환경(uvicorn/gunicorn, EB 등)에서 이 모듈의 app 객체를 로드하여 실행
"""

import time

from fastapi import FastAPI, Request
from starlette.responses import Response

from app.routers import chat, history, health
from app.core.request_id import (
    REQUEST_ID_HEADER,
    generate_request_id,
    set_request_id,
)
from app.core.logger import get_logger


logger = get_logger("Chatbot-law-prod.middleware.request_id")


## app 객체 생성
app = FastAPI(title="Chatbot Law API")


## 요청/응답을 가로채는 공통처리
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    start = time.perf_counter()

    ## 요청 헤더에 X-Request-ID가 있으면 사용 
    ## 없으면 생성
    request_id = request.headers.get(REQUEST_ID_HEADER) or generate_request_id()
    ## 저장
    set_request_id(request_id)

    try:
        response: Response = await call_next(request)
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        ## logger 포맷에 request_id가 자동 포함됨
        logger.info(
            f'{request.method} {request.url.path} complated in {duration_ms: .2f}ms'
        )
        ## 다음 요청에 섞이지 않게 초기화
        set_request_id(None)

    ## 응답헤더에 X-Request-ID 포함하여 클라이언트에 전송
    response.headers[REQUEST_ID_HEADER] = request_id
    return response  
      

## 라우터 등록 (라우트 테이블에 등록)
app.include_router(chat.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(health.router)