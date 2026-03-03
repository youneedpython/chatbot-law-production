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
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.routers import chat, history, health
from app.core.request_id import (
    REQUEST_ID_HEADER,
    generate_request_id,
    set_request_id,
)
from app.core.logger import get_logger
from app.core.config import METRICS_ENABLED, validate_runtime_env


logger = get_logger("Chatbot-law-prod.middleware.request_id")
validate_runtime_env()  ## 앱 실행 시점에 환경변수 검증

## app 객체 생성
app = FastAPI(title="Chatbot Law API")

## CORS
origins = [
    'https://d19b4mxgdd1vkt.cloudfront.net',  ## frontend domain
    # 'https://api-chatbot-law-dev.store',          ## 커스텀 도메인
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False, 
    allow_methods=['*'],
    allow_headers=['*'],
)

## 요청/응답을 가로채는 공통처리
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    start = time.perf_counter()

    ## 요청 헤더에 X-Request-ID가 있으면 사용 
    ## 없으면 생성
    request_id = request.headers.get(REQUEST_ID_HEADER) or generate_request_id()
    ## 저장
    set_request_id(request_id)


    ## 계측 코드 ##################################
    ## (추가) 요청 단위 metrics 저장소 준비 
    request.state.metrics = {}
    ##############################################

    response = None

    try:
        response: Response = await call_next(request)
        return response
    finally:
        duration_ms = int((time.perf_counter() - start) * 1000)

        ## logger 포맷에 request_id가 자동 포함됨
        logger.info(
            f'{request.method} {request.url.path} completed in {duration_ms}ms'
        )
        

        ## 계측 코드 ##################################
        ## (추가) /health는 제외(로그 오염 방지)
        ## (추가) 운영용 요청 요약 METRIC 로그
        if METRICS_ENABLED:
            path = request.url.path
            # health는 제외 권장 (헬스체크로 로그 오염 방지)
            if path != "/health":
                m = getattr(request.state, "metrics", {}) or {}
                parts = [
                    "METRIC|event=request",
                    f"path={path}",
                    f"method={request.method}",
                ]

                ## 추가: provider/model
                if "provider" in m:
                    parts.append(f"provider={m['provider']}")
                if "model" in m:
                    parts.append(f"model={m['model']}")

                parts.append(f"ms_total={duration_ms}")
                
                # 라우터에서 기록한 값이 있으면 함께 출력
                for key in (
                    "ms_db_user",
                    "ms_history_load",
                    "ms_ask_llm",
                    "ms_db_assistant",
                ):
                    if key in m:
                        parts.append(f"{key}={m[key]}")
                logger.info("|".join(parts))
        ##############################################


        ## 응답헤더에 X-Request-ID 포함하여 클라이언트에 전송
        if response is not None:
            response.headers[REQUEST_ID_HEADER] = request_id

        ## 다음 요청에 섞이지 않게 초기화
        set_request_id(None)
        
      

## 라우터 등록 (라우트 테이블에 등록)
app.include_router(chat.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(health.router)