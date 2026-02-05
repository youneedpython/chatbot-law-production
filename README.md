# Chatbot Law – Production

전세사기 피해자를 위한 **법률 상담 AI 챗봇 (Production Backend)**  
FastAPI 기반 백엔드와 React 프론트엔드로 구성된 **실서비스 지향 프로젝트**입니다.  

본 프로젝트는 단순한 LLM 데모가 아닌,  
**운영 환경에서 안정적으로 동작하는 API 서버 구축**을 목표로 설계되었습니다.


본 프로젝트는 기능 단위 릴리즈와 안정화 패치 릴리즈를 명확히 구분하여,
운영 기준선을 중심으로 점진적으로 확장되는 구조를 지향합니다.

---

## 📌 Project Overview

This project represents a production-stable baseline with verified dev/prod parity and applied database migrations.  
본 프로젝트는 dev와 prod 환경의 동기화가 검증되었고,
데이터베이스 마이그레이션이 적용된 안정적인 프로덕션 기준선을 제공합니다.


- **Current Version:** v0.5.1
- **Deployment:** 
  - Backend: AWS Elastic Beanstalk (Production)
  - Frontend: S3 + CloudFront (Production)
- **Focus:** 
  - Backend & Frontend CI/CD 안정화
  - Production 배포 표준 확립 (Frontend 포함)
- **RAG (Vector DB):** Pinecone 기반 RAG 파이프라인 구현 및 안정화 완료

---

## 🧱 Architecture

### Current (v0.5.1)

```text
Frontend
└─ GitHub Actions (CI/CD)
   └─ S3
      └─ CloudFront
            ↓
Backend
└─ GitHub Actions (CI/CD)
   └─ Application Load Balancer (ALB)
      └─ Elastic Beanstalk
         └─ RDS (PostgreSQL, migrated from SQLite)
``` 

### Current Extensions

```text
Backend
└─ RAG (Vector Store, Embeddings, Citation Rendering)
```
---

## ✅ Implemented Features
- Backend API (FastAPI)
- Frontend SPA (React)
- Backend CI/CD (Elastic Beanstalk)
- Frontend CI/CD (S3 + CloudFront)
- Request ID 기반 트레이싱

## 🔜 Planned Core Features
- Streaming RAG 응답 처리
- 법률 문서 기반 응답 신뢰도 및 출처 UX 고도화
- 대화 히스토리 기반 응답 품질 개선

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
- GitHub Actions (CI/CD, OIDC)
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
- 로드밸런서 헬스 체크 및 CloudFront 경로 검증 용도

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
VITE_APP_ENV=dev | prod    # build-time environment flag
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
- GitHub Actions 기반 자동 배포
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

### Core (In Progress)
- RAG 응답 품질 고도화
- 대화 히스토리 기반 응답 품질 개선

### Next (v0.6.x)
- Streaming RAG 응답 처리
- Prompt 전략 고도화
- 응답 신뢰도 및 출처 표현 UX 개선

### Future
- 인증 / Rate limiting
- Admin / Monitoring UI

---

## ⚠️ Legal Notice
본 서비스는 법률 자문을 제공하지 않으며,
일반적인 정보 제공을 목적으로 합니다.
구체적인 법률 판단은 반드시 전문가와 상담하시기 바랍니다.

---

## 📄 License

Internal / Portfolio Project