# Chatbot Law – Production

전세사기 피해자를 위한 **법률 상담 AI 챗봇 (Production Backend)**  
FastAPI 기반 백엔드와 React 프론트엔드로 구성된 **실서비스 지향 프로젝트**입니다.  

본 프로젝트는 단순한 LLM 데모가 아닌,  
**운영 환경에서 안정적으로 동작하는 API 서버 구축**을 목표로 설계되었습니다.

---

## 📌 Project Overview

This release represents a production-stable baseline with verified
dev/prod parity and database migration applied.  
이번 릴리스는 dev와 prod 환경의 동기화가 검증되었고, 데이터베이스 마이그레이션이 적용된 안정적인 프로덕션 기준선입니다.

- **Current Version:** v0.4.2
- **Deployment:** AWS Elastic Beanstalk (Production)
- **Focus:** Observability · 안정성 · 운영 기준 설계
- **RAG / CI/CD:** 차기 버전에서 확장 예정



---

## 🧱 Architecture

### Current (v0.4.2)

```text
Frontend
└─ S3 + CloudFront
   ↓
Backend
└─ Application Load Balancer (ALB)
   └─ Elastic Beanstalk
      └─ RDS (PostgreSQL, migrated from SQLite)
``` 

### Planned

```text
Backend Extensions
└─ RAG (Vector Store, Embeddings)
```
---

## 🛠 Tech Stack

### Backend
- Python 3.11
- FastAPI
- Uvicorn
- SQLAlchemy
- Alembic
- LangChain (LLM orchestration)
- OpenAI API

### Frontend
- React
- Vite
- Fetch API

### Infrastructure
- AWS Elastic Beanstalk (EC2, ALB)
- S3 + CloudFront
- LangSmith (Tracing)

---

## 🔎 Production Networking & Observability

### ✅ Request ID 기반 추적
- 모든 요청에 `X-Request-ID` 전달 또는 자동 생성
- 로그, 응답 헤더, 내부 처리 전 과정에서 동일 ID 사용
- 운영 환경 디버깅 및 장애 추적 가능

```bash
curl -X POST http://localhost:8000/api/chat/1234 \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: test-request-id-001" \
  -d '{"message":"전세사기 피해자 설명해줘"}'
```

---

## ❤️ Health Check

```
GET /health
```

- 서비스 기본 생존 상태 확인
- 로드밸런서 / CloudFront 헬스 체크 용도

### Planned Endpoints (Future Enhancement)
| Endpoint              | Description                     |
|-----------------------|---------------------------------|
| `/health/liveness`    | 프로세스 생존 여부               |
| `/health/readiness`   | DB / 외부 의존성 준비 상태       |


---

## 📚 API Documentation

- Swagger UI: `/docs`
- OpenAPI spec: `/openapi.json`

---

## ⚙️ Environment Variables

### Backend

| Variable                | Description            |
|-------------------------|------------------------|
| `APP_ENV`               | Runtime environment (`dev` / `prod`) |
| `OPENAI_API_KEY`        | OpenAI API key         |
| `OPENAI_MODEL`          | LLM model name         |
| `DATABASE_URL`          | Database connection URL |
| `LANGCHAIN_TRACING_V2`  | Enable LangChain tracing (`true` / `false`) |
| `LANGCHAIN_PROJECT`     | LangSmith project name |
| `LANGSMITH_API_KEY`     | LangSmith API key      |


### Frontend
```env
VITE_API_BASE_URL=/api
```

---

## 🌐 CORS & Strategy

### Local
- Vite dev server /api proxy 사용
- 브라우저 기준 same-origin → CORS 문제 없음

### Production
- CloudFront / ALB 기준 /api 유지
- Backend에서 명시적 CORS 정책 적용
- Frontend–Backend origin 분리를 고려한 설계

---

## 🚀 Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 📦 Deployment

### Frontend
- S3 Static Website Hosting
- CloudFront CDN distribution

### Backend
- AWS Elastic Beanstalk
- Application Load Balancer (ALB)

### Database
- PostgreSQL

---

## 📂 Repository Structure
``` text
.
├── backend
│   ├── app
│   ├── alembic
│   └── ...
├── frontend
│   ├── src
│   └── ...
├── README.md
└── CHANGELOG.md
```

---

## 🧭 Roadmap

### Next
- CI/CD automation
- Deployment pipeline stabilization

### Future
- RAG (Vector Store + Retrieval)
- Authentication / Rate limiting

---

## 📄 License

Internal / Portfolio Project