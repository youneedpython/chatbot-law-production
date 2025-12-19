# chatbot-law-prod

전세사기 피해자를 위한 **세션 기반 법률 상담 챗봇** 프로젝트입니다.

본 프로젝트는 단순한 PoC를 넘어, **실제 서비스로 확장 가능한 아키텍처 설계와 단계적 진화**를 목표로 합니다.

---

## 📌 Project Vision

- 전세사기 피해자가 **상담 맥락을 유지한 채** 법률 정보를 탐색할 수 있는 챗봇
- Frontend 중심 상태 관리에서 벗어나 **Backend를 Source of Truth로 전환**
- 향후 **RAG(법령·판례)**, **멀티 디바이스**, **케이스 관리**로 확장 가능한 구조

---

## 🏗️ Architecture Overview

```text
[ React (Vite) ]
        │
        ▼
[ FastAPI Backend ]
        │
        ├─ Conversation / Message API
        ├─ LLM Orchestration Layer
        │
        ▼
[ SQLite Database ]
```

- **Frontend**: 사용자 인터페이스 및 세션 URL 관리
- **Backend**: 대화 흐름 제어, 히스토리 저장, LLM 호출 오케스트레이션
- **Database**: 대화방(conversation)과 메시지(message)의 영속 저장

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

### LLM
- OpenAI (integration planned)
- LLM orchestration layer implemented (stubbed in v0.4.0)

---

## 🚀 Key Features (up to v0.4.0)

### 1. Session-based Chat
- URL 기반 session_id 생성 (`/chat/{session_id}`)
- 새로고침 및 재접속 시 대화 유지

### 2. Backend-driven Conversation History (v0.4.0)
- SQLite 기반 대화 히스토리 영속화
- `conversation_id = session_id` 설계
- Source of Truth를 frontend(localStorage) → backend(DB)로 전환
- 멀티 디바이스 대응 가능한 구조

### 3. Clear Chat Orchestration Flow

```text
User Input
   ↓
Save User Message (DB)
   ↓
call_llm()  ← LLM Orchestration Layer
   ↓
Save Assistant Message (DB)
   ↓
Return Response
```

- LLM 호출 로직을 별도 함수로 분리
- 향후 RAG / 히스토리 기반 응답으로 확장 가능

---

## 📡 API Endpoints

### Chat

```http
POST /api/chat/{session_id}
```

- 사용자 메시지 전송 및 응답 생성

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
- **v0.3.0**: UX improvements & chat history UI
- **v0.4.0**: Backend-driven session history with SQLite

---

## 🔮 Next Steps

### v0.4.1
- Actual LLM integration (`call_llm`)
- Error handling & loading UX

### v0.5.0
- RAG with statutes and case law
- History-aware response generation
- Case-based legal consultation model

---

## 📄 Notes

- This project emphasizes **architecture and evolution**, not just feature delivery.
- v0.4.0 focuses on backend history design and service-grade structure.

---

## 📜 License

MIT