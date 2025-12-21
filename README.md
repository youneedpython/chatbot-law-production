# chatbot-law-prod

전세사기 피해자를 위한 **세션 기반 법률 상담 챗봇 (Service-ready Backend)** 프로젝트입니다.

본 프로젝트는 PoC 수준을 넘어,  
**관측가능성(Observability)·운영 가능성·점진적 확장**을 고려한  
**실서비스 지향 백엔드 아키텍처**를 목표로 합니다.

---

## 📌 Project Vision

- 전세사기 피해자가 **상담 맥락을 유지한 채** 법률 정보를 탐색
- Frontend 상태 의존 → **Backend를 Source of Truth**로 전환
- **Request Tracing / Logging / Health Check**를 포함한 운영 기반 확보
- 향후 **RAG(법령·판례)**, **케이스 관리**, **운영 지표**로 확장

---

## 🏗️ Architecture Overview (v0.4.2)

```text
[ React (Vite) ]
        │
        ▼
[ FastAPI Backend ]
        │
        ├─ Chat / Conversation API
        ├─ Session-based History (SQLite)
        ├─ Request ID Middleware
        ├─ Structured Logging
        ├─ Health / Readiness Endpoints
        │
        ▼
[ SQLite Database ]
```

---
### 핵심 변화 (v0.4.2)

- 모든 요청에 **request_id 기반 추적 가능**
- 로그 → **운영 관점에서 해석 가능한 구조**로 전환
- 배포/운영을 고려한 **health / readiness 분리**

---

## 🧱 Tech Stack

### Frontend
- React + Vite
- React Router (session-based routing)
- Fetch API

### Backend
- FastAPI
- SQLAlchemy
- SQLite
- Custom Middleware (Request ID)
- Structured Logging (JSON-like)

### LLM
- OpenAI (integration planned)
- LLM orchestration layer 분리 완료
- RAG 연동은 v0.5.x에서 도입


## 🚀 Key Features (up to v0.4.2)

### 1. Session-based Chat

- URL 기반 session_id (`/chat/{session_id}`)
- 새로고침 / 재접속 시 대화 유지
- `conversation_id == session_id` 설계

---

### 2. Backend-driven Conversation History (v0.4.0)

- SQLite 기반 대화 히스토리 영속화
- Frontend(localStorage) → Backend(DB) 전환
- 멀티 디바이스 확장 가능한 구조

---

### 3. Request ID Middleware (v0.4.2)

- 모든 요청에 `X-Request-ID` 자동 부여
- 클라이언트가 전달한 ID는 그대로 전파
- 응답 헤더 + 로그에 동일 ID 유지

```text
Request
 └─ X-Request-ID
      ├─ API Logs
      ├─ LLM Invocation Logs
      └─ Error Logs
```
- 👉 문제 추적 / 장애 분석 / 운영 대응 가능

---

### 4. Structured Logging (v0.4.2)

- `print()` 제거 → 프로젝트 로거 통합
- request_id 중심 로그 포맷
- API / Service / Repository 계층 로그 분리

예:

```text
[request_id=abc123] chat.create_message.success
```

---

### 5. Health & Readiness Endpoints (v0.4.2)

```http
GET /health
```

- 서비스 기본 생존 상태 확인
- (v0.4.3 예정) `/health/liveness`, `/health/readiness` 분리

---

## 🧱 Tech Stack

### Frontend
- React + Vite
- React Router (session-based routing)
- Fetch API

### Backend
- FastAPI
- SQLAlchemy
- SQLite
- Custom Middleware (Request ID)
- Structured Logging

### LLM
- OpenAI (integration planned)
- LLM orchestration layer 분리 완료
- Vector Store / RAG 연동은 v0.5.x에서 도입

---

## 📡 API Endpoints

### Health

```http
GET /health
```

Response:
```json
{
  "status": "ok",
  "service": "chatbot-law-prod"
}
```

---

### Chat

```http
POST /api/chat/{session_id}
```

- 사용자 메시지 저장
- LLM 호출
- 응답 메시지 저장 후 반환

---

### Conversation History

```http
GET /api/conversations/{session_id}/messages
```

Response:
```json
{
  "messages": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ],
  "has_more": false
}
```

---

## 🗄️ Database Schema (Simplified)

### conversations
- id (session_id)
- created_at
- updated_at

### messages
- conversation_id
- seq
- role (user / assistant)
- content
- created_at

---

## ▶️ How to Run (Development)

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m app.init_db
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🧭 Version Highlights

- **v0.1.0**: Production MVP scaffold
- **v0.2.0**: Session-based chat flow
- **v0.3.0**: UX & chat history UI
- **v0.4.0**: Backend-driven history (SQLite)
- **v0.4.1**: Repository 안정화 & 동시성 보강
- **v0.4.2**: **Observability (request_id, logging, health)** ✅

---

## 🔮 Next Steps

### v0.4.3

- API / concurrency smoke tests
- 운영 Runbook 문서화
- 기본 배포 검증

---

### v0.5.x

- Vector Store + Embedding 기반 RAG
- 법령/판례 검색 파이프라인
- History-aware response generation
- 운영 지표(Log → Metric) 확장

---

## 📄 Notes

- 이 프로젝트는 **기능 나열이 아닌 “서비스로 가는 진화 과정”**을 기록합니다.
- v0.4.x는 **배포 가능한 안정성 확보**
- v0.5.x부터 **법률 도메인 지능화(RAG)**가 본격 도입됩니다.

---

## 📜 License
MIT
