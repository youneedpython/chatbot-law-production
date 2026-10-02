# 🚀 로컬 개발 환경 설정 (Local Development)

본 가이드는 로컬 개발 머신에서 **Chatbot Law** 백엔드(FastAPI) 및 프론트엔드(React/Vite)를 설정하고 실행하는 절차를 설명합니다.

---

## 📋 사전 요구 사항 (Prerequisites)

- **Python**: `3.11.x` 권장
- **Node.js**: `v18.x` 또는 `v20.x` 이상 (npm 포함)
- **Git**: 최신 버전
- **OpenAI API Key**: LLM 질의응답 및 임베딩 생성용
- **Pinecone API Key**: 벡터 검색용 (선택 사항, 로컬 Mocking 또는 Dev 인덱스 사용)

---

## 📂 프로젝트 구조

```text
chatbot-law-production/
├── backend/                  # FastAPI 백엔드
│   ├── alembic/              # DB 마이그레이션 스크립트
│   ├── app/                  # 애플리케이션 핵심 소스 (routers, service, models 등)
│   ├── data/                 # 법률 원문(docx) 및 인덱스 매니페스트
│   ├── scripts/              # 데이터 인덱싱 파이프라인
│   ├── tests/                # 테스트 코드
│   ├── .env.example          # 환경 변수 템플릿
│   └── requirements.txt      # Python 의존성 목록
├── frontend/                 # React SPA (Vite)
│   ├── src/                  # 컴포넌트, API 클라이언트, 스타일
│   ├── package.json          # Node.js 의존성
│   └── vite.config.js        # Vite 빌드 및 프록시 설정
└── docs/                     # 기술 문서 및 이미지
```

---

## 🐍 1. 백엔드 (FastAPI) 설정 및 실행

### 1) 가상환경 생성 및 활성화
`backend` 디렉터리로 이동하여 Python 가상환경을 생성하고 활성화합니다.

```bash
cd backend

# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 가상환경 활성화 (macOS / Linux / Bash)
source venv/bin/activate
```

### 2) 패키지 의존성 설치
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3) 환경 변수 파일(`.env`) 생성
`backend/.env.example`을 복사하여 `backend/.env` 파일을 생성하고 필요한 값을 입력합니다.

```bash
cp .env.example .env
```

**최소 구동 필수 설정 (`backend/.env`)**:
```env
ENV=local
OPENAI_API_KEY=sk-proj-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./dev.db

# Vector DB (선택 - 실시간 검색 테스트 시 필요)
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=chatbot-law-dev

# LangSmith 추적 (선택)
LANGCHAIN_TRACING_V2=false
```

### 4) 데이터베이스 마이그레이션 실행 (Alembic)
로컬 SQLite(`dev.db`)에 최신 테이블 스키마(`conversations`, `messages`)를 생성합니다.

```bash
alembic upgrade head
```

### 5) 백엔드 개발 서버 실행
```bash
uvicorn app.main:app --reload --port 8000
```
- API 서버 기본 주소: `http://localhost:8000`
- 대화형 Swagger 문서: `http://localhost:8000/docs`
- 대안 ReDoc 문서: `http://localhost:8000/redoc`

### 6) 헬스체크 검증
새 터미널에서 정상 구동 여부를 확인합니다:
```bash
curl http://localhost:8000/health
# 응답: {"status":"ok","service":"chatbot-law-prod"}
```

---

## ⚛️ 2. 프론트엔드 (React + Vite) 설정 및 실행

프론트엔드 개발 서버는 `vite.config.js`에 설정된 로컬 프록시를 통해 브라우저의 `/api/*` 요청을 `http://localhost:8000/api/*`로 투명하게 전달하므로, 로컬 환경에서 CORS 설정 변경 없이 바로 연동됩니다.

### 1) 패키지 설치
`frontend` 디렉터리로 이동하여 npm 패키지를 설치합니다:

```bash
cd ../frontend
npm install
```

### 2) 개발 서버 실행
```bash
npm run dev
```

터미널에 안내되는 로컬 URL(`http://localhost:5173`)로 브라우저에 접속합니다.

---

## 🧪 3. 테스트 실행

백엔드의 무결성 및 기본 헬스체크 동작을 검증하기 위해 pytest를 실행합니다.

```bash
cd backend
pytest -v
```

---

## 💡 자주 발생하는 문제 및 해결 방법 (Troubleshooting)

### Q1. `ModuleNotFoundError: No module named 'app'` 오류가 발생합니다.
- **원인**: 실행 위치가 `backend` 디렉터리가 아니거나 파이썬 경로가 지정되지 않았습니다.
- **해결**: 반드시 `backend` 폴더 내에서 명령어를 실행하거나, `PYTHONPATH=.`를 지정하여 실행합니다:
  ```bash
  # Windows PowerShell
  $env:PYTHONPATH="."
  uvicorn app.main:app --reload --port 8000
  ```

### Q2. `OPENAI_API_KEY environment variable is required.` 런타임 에러
- **원인**: `backend/.env` 파일에 유효한 OpenAI API 키가 지정되지 않았습니다.
- **해결**: `app/core/config.py`의 `validate_runtime_env()`는 서버 기동 시 필수 키를 검증합니다. `.env` 파일에 `OPENAI_API_KEY`를 설정하세요.

### Q3. 프론트엔드에서 API 호출 시 404가 발생합니다.
- **원인**: 백엔드 서버(`8000`번 포트)가 켜져 있지 않거나 프록시 타겟이 잘못 지정되었습니다.
- **해결**: 백엔드가 `http://localhost:8000`에서 실행 중인지 확인하고, `frontend/vite.config.js`의 proxy 설정을 점검하세요.
