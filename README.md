# 🏠 전세사기 피해 상담 챗봇 (Production MVP)

전세사기 피해자를 위한 **상담용 AI 챗봇**입니다.  
React + FastAPI 기반의 Production MVP로, 세션 기반 상담 흐름을 제공합니다.

---

## 📌 Project Overview

이 프로젝트는 전세사기 피해자가 기본적인 법적 대응 방향을 이해하고,  
상담 흐름을 세션 단위로 이어갈 수 있도록 돕는 AI 챗봇 서비스입니다.

- Frontend: React (Vite)
- Backend: FastAPI
- LLM: OpenAI 기반 (LangChain)
- Session 관리: URL Path Parameter (`/chat/{session_id}`)

---


## 🧱 Architecture

```
CHATBOT-LAW-PROD
├── backend
│   ├── app
│   │   ├── api          # FastAPI 라우터
│   │   ├── core         # 설정, 로깅
│   │   ├── service      # LLM 비즈니스 로직
│   │   └── main.py      # FastAPI 엔트리포인트
│   ├── data
│   │   └── keyword_dictionary.json
│   ├── .env.example
│   └── requirements.txt
│
├── frontend
│   ├── src
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   └── vite.config.js
│
└── README.md
```

---

## 🚀 Key Features (v0.2.0)

### ✅ Session-based Chat
- 첫 질문 시 `session_id` 자동 생성
- 이후 모든 대화는 동일한 세션으로 유지
- URL 구조:  
  ```
  /chat/{session_id}
  ```

### ✅ Production MVP Structure
- Frontend / Backend 명확한 책임 분리
- LLM 로직 분리 (`service` 계층)
- 환경별 설정 관리 (`ENV=local|prod`)

### ✅ Health Check
- Backend 상태 확인용 엔드포인트 제공
  ```
  GET /health

---

## ⚙️ 기술 스택

### Frontend
- React (Vite)
- Fetch API
- useState 기반 상태 관리
- Vite proxy (/api → backend)

### Backend
- FastAPI
- Uvicorn
- LLM API (OpenAI)
- REST API (/health, /chat)
- LangChain (Conversation Chain)

---

## 🔌 API Endpoints

### Health Check
```
GET /health
```

**Response**
```json
{ "status": "ok" }
```
---

### Chat
```
POST /chat/{session_id}
```

**Request Body**
```json
{
  "message": "전세사기 피해 구제 방안은?"
}
```

**Response**
```json
{
  "answer": "...",
  "session_id": "uuid"
}
```

#### Design Decision
- session_id를 Path Parameter로 사용한 이유
  - URL 공유 및 북마크 가능
  - 세션 상태를 명확히 식별
  - RESTful한 리소스 표현

---

## 🚀 로컬 실행 방법

### Backend
cd backend  
pip install -r requirements.txt  
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload  

Swagger: http://localhost:8000/docs  

---

### Frontend
cd frontend  
npm install  
npm run dev  

Web: http://localhost:5173   
/api/* 요청은 자동으로 backend(localhost:8000)로 프록시됨

---

## 🔐 환경변수
- 실제 .env 파일은 Git에 포함되지 않음
- backend/.env.example 참고

---

## ⚠️ 주의
- 본 챗봇은 법률 자문을 제공하지 않습니다
- 실제 법적 판단이나 소송은 반드시 전문가(변호사, 공공기관) 상담 필요
- LLM 응답은 참고용 정보로만 사용해야 합니다

---

## 🏷 Versioning

- **v0.1.0**: PoC (Streamlit 기반)
- **v0.2.0**: Production MVP  
  - React + FastAPI 전환  
  - 세션 기반 상담 구조 도입

---

## 🔮 Next Steps

- v0.3.0
  - 대화 히스토리 조회 API
  - 스트리밍 응답(SSE)
  - UX 개선 (로딩, 에러 처리)