"""
routers/health.py

서비스 헬스체크(Health Check) 엔드포인트 라우터

엔드포인트
- GET /health
  - 서비스가 정상 응답 가능한지 단순 확인용
  - AWS EB / ALB 헬스체크 및 모니터링에 사용

주의
- 외부 의존성(DB, OpenAI 등)까지 검증할지 여부는 운영 정책에 따라 분리 가능
  (현재는 lightweight health check)
"""



from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)

@router.get("")
def health_check():
    return {
        "status": "ok",
        "service": "chatbot-law-prod",
    }