# Chatbot Law – Production

전세사기 피해자를 위한 **법률 상담 AI 챗봇 (Production)**  
FastAPI 기반 백엔드 + React(Vite) 프론트엔드로 구성된 실서비스 지향 프로젝트입니다.

---

## 📌 Project Overview

- **목표**
  - 전세사기 피해자에게 신뢰 가능한 법률 정보 제공
  - 운영 환경에서 추적 가능한 관측가능성(Observability) 확보
  - 향후 RAG(Vector Store) 기반 고도화 확장

- **현재 버전**
  - **v0.4.2** – Observability 기반 안정화 완료

---

## 🧱 Architecture

```
Frontend (React + Vite)
  └─ S3 + CloudFront (예정)
       ↓ HTTP
Backend (FastAPI)
  └─ AWS Elastic Beanstalk
       ↓
   SQLite / RDB (향후 확장)
```

---

## 🛠 Tech Stack

### Backend
- Python 3.11
- FastAPI
- Uvicorn
- LangChain
- OpenAI API
- (Optional) Pinecone / Vector Store (v0.5.x 예정)

### Frontend
- React
- Vite
- React Router
- Fetch API

### Infrastructure
- AWS Elastic Beanstalk (Backend)
- AWS S3 + CloudFront (Frontend 예정)
- GitHub Projects / Issues
- LangSmith (Tracing)

---

## 🔎 Observability (v0.4.2 핵심)

### ✅ Request ID 기반 추적
- 모든 요청에 `X-Request-ID` 자동 생성 또는 전파
- 응답 헤더 및 로그에 동일한 request_id 기록

```bash
curl -X POST http://localhost:8000/api/chat/1234 \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: test-request-id-001" \
  -d '{"message":"전세사기 피해자 설명해줘"}'
```

---

## ❤️ Health & Readiness Endpoints (v0.4.2)

```http
GET /health
```

- 서비스 기본 생존 상태 확인

- v0.4.3 예정
| Endpoint | Description |
|--------|-------------|
| `/health/liveness` | 프로세스 생존 여부 |
| `/health/readiness` | DB / 외부 의존성 준비 상태 |

---

## 📚 API Documentation

- Swagger UI:  
  ```
  http://localhost:8000/docs
  ```

---

## ⚙️ Environment Variables

### Backend

| 변수명 | 설명 |
|------|------|
| `APP_ENV` | dev / prod |
| `OPENAI_API_KEY` | OpenAI API Key |
| `OPENAI_MODEL` | 사용 모델 |
| `DATABASE_URL` | DB URL |
| `LANGCHAIN_TRACING_V2` | true / false |
| `LANGCHAIN_PROJECT` | LangSmith 프로젝트 |
| `LANGSMITH_API_KEY` | LangSmith API Key |
| `PINECONE_API_KEY` | (v0.5.x 예정) |

### Frontend

```env
VITE_API_BASE_URL=/api
```

- 개발 환경
  - Vite proxy(/api) → http://localhost:8000
  - 브라우저 CORS 회피
- 운영 환경
  - CloudFront / Reverse Proxy 기준 /api 유지
  - 또는 실제 Backend 도메인 사용


---

## 🌐 CORS & Proxy 설명 (중요)
- 개발 중 /api로 호출 시:
  - Vite dev server가 프록시 역할
  - 브라우저 기준 same-origin → CORS 발생 ❌
- http://localhost:8000 직접 호출 시:
  - Origin 불일치 → CORS 에러 발생
  - 해결 방법:
    - Vite proxy 사용 (개발)
    - Backend CORS 설정 or Reverse Proxy 사용 (운영)

---

## 🚀 Running Locally

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

접속
```bash
http://localhost:5173
```

---

## 📦 Deployment
### Backend – AWS Elastic Beanstalk
- Python 3.11 / Amazon Linux 2023
- backend.zip 업로드 방식
- 환경 변수: EB → Configuration → Environment variables

### Frontend – S3 + CloudFront (예정)

```bash
npm run build
```
- dist/ 폴더를 S3에 업로드
- CloudFront에서 SPA 라우팅 설정 필요
- 403/404 → index.html

---

## Repository Structure
```text
.
├── backend
│   ├── app
│   ├── dev.db
│   └── ...
├── frontend
│   ├── src
│   │   └── api/client.js
│   ├── vite.config.js
│   └── ...
├── README.md
└── CHANGELOG.md
```

---

## 🧭 Version Roadmap
### v0.4.2 (Current)
- Request ID 기반 추적
- Health Check 분리
- Observability 안정화
- EB 배포 성공

### v0.4.3
- 운영 Runbook 문서화
- API / 동시성 테스트 추가

### v0.5.x
- Vector Store + RAG 적용
- 법률 문서 임베딩
- 검색 기반 응답 고도화

---

## 📄 License

Internal / Portfolio Project


