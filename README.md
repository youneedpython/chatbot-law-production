# 🏠 전세사기 피해 상담 챗봇 (Production MVP)

전세사기 피해자를 위한 **법률·제도 안내 중심 AI 상담 챗봇**입니다.  
본 프로젝트는 PoC(Streamlit 기반)를 거쳐,  
현재 **Production MVP (React + FastAPI + LLM Backend)** 구조로 전환 중입니다.

---

## 📌 프로젝트 목적

- 전세사기 피해자가 **초기 대응 단계에서 필요한 정보**를 빠르게 확인할 수 있도록 지원
- 법률 절차, 신고 방법, 보증금 회수 가능성 등 **정책·제도 기반 정보 제공**
- LLM을 활용하되, **법률 자문이 아닌 정보 안내용 챗봇**으로 설계

---

## 🧱 프로젝트 구조 (Monorepo)

```text
CHATBOT-LAW-PROD
├─ backend/               # FastAPI + LLM Backend
│  ├─ app/
│  │  ├─ main.py          # FastAPI 엔트리포인트
│  │  ├─ core/            # 설정, 공통 로직
│  │  ├─ service/         # LLM 서비스 로직
│  ├─ .env.example        # 환경변수 예시 (실제 키 없음)
│  ├─ requirements.txt
│
├─ frontend/              # React (Vite)
│  ├─ src/
│  │  ├─ App.jsx          # 메인 UI
│  │  ├─ main.jsx         # React 엔트리
│  ├─ index.html
│  ├─ package.json
│  ├─ vite.config.js      # API 프록시 설정
│
├─ .gitignore
└─ README.md
```

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

---

## 🔌 API 명세

### Health Check
GET /health

Response:
{ "status": "ok" }

---

### Chat
POST /chat

Request:
{ "message": "전세사기 피해자 구제 방안은?" }

Response:
{ "answer": "전세사기 피해자를 위한 구제 방안은 다음과 같습니다..." }

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

## 🧭 개발 단계
- PoC (Streamlit 기반) 완료
- Production MVP (React + FastAPI) 개발 중
- Production 배포 예정