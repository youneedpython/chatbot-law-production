# Chatbot Law Production

**전세사기 피해자를 위한 법률·행정 절차 안내 AI 서비스입니다.**

사용자가 질문을 입력하면 관련 법령 문서를 검색하고, 근거가 확인된 절차와 기관 정보를 대화형 답변으로 제공합니다. 답변에는 검색된 법령 조항을 가리키는 인용 정보가 함께 반환됩니다.

![상담 초기 화면](docs/images/service_preview_blank.png)

> 이 서비스는 공인된 법률 자문이나 법적 대리 행위를 제공하지 않습니다. 실제 사건은 대한법률구조공단, 전세피해지원센터 또는 전문 변호사와 상담해야 합니다.

| | 내용 |
|---|---|
| 화면 | React SPA 기반 상담 화면과 세션별 대화 이력 |
| 데이터 | 전세사기피해자 지원 및 주거안정에 관한 특별법과 같은 법 시행령 원문 |
| 모델 | OpenAI LLM(기본 `gpt-4o-mini`) / `text-embedding-3-large` 임베딩(Index 3072차원) |
| 검색 | Pinecone Vector Store, 기본 `RAG_TOP_K=5` |
| 배포 | S3 · CloudFront · Elastic Beanstalk · RDS PostgreSQL |

**더 읽기**: [Wiki](https://github.com/youneedpython/chatbot-law-production/wiki) · [Releases](https://github.com/youneedpython/chatbot-law-production/releases) · [CHANGELOG.md](CHANGELOG.md)

---

## 사용 영상

Local 환경에서 Pinecone Index `chatbot-law-prod`에 연결해 2026-10-06에 녹화했습니다.

**PC (35초)** — 초기 화면 → 추천 질문 선택 → 답변과 조항 인용 → 이어서 질문 입력 → 답변 복사

https://github.com/user-attachments/assets/b95a4a66-b910-4341-9602-f5a8283ca49a

**모바일 (34초)** — 같은 흐름을 390px 화면에서

https://github.com/user-attachments/assets/cb9309e0-e147-4b78-bd01-c5f89ed2d067

- 답변은 번호 목록 형식이며, 문장 끝에 근거 조항을 `[전세사기피해자법 제6조 제1항]`처럼 표시합니다.
- 조항 인용은 모든 답변에 붙지는 않습니다. 자세한 내용은 [Roadmap과 한계](https://github.com/youneedpython/chatbot-law-production/wiki/Roadmap과-한계)에 있습니다.

---

## 주요 기능

### 1. 법률 문서 기반 RAG

- 법령을 법률명·조문·항 단위 메타데이터와 함께 검색합니다.
- 검색된 근거를 바탕으로 답변하며, 근거가 부족한 법률 판단은 생성하지 않습니다.
- 법률 원문은 `backend/data/raw_docs/`에 저장된 문서 2개(특별법, 시행령)를 인덱싱한 결과를 사용합니다.

### 2. 인용 정보가 포함된 답변

- LLM 답변의 `⟦n⟧` 앵커와 API의 `sources[n].id`를 같은 번호로 관리합니다.
- Frontend는 앵커를 법률명과 조항명으로 표시합니다.
- 자세한 흐름은 [서비스 소개](https://github.com/youneedpython/chatbot-law-production/wiki/서비스-소개)와 [핵심 로직](https://github.com/youneedpython/chatbot-law-production/wiki/핵심-로직)을 참고합니다.

### 3. 세션 기반 대화 이력

- 대화 세션과 메시지를 Backend 데이터베이스에 저장합니다.
- 세션별 메시지를 조회하고 이어서 상담할 수 있습니다.
- 브라우저의 임시 상태만을 유일한 저장소로 사용하지 않습니다.

### 4. 운영을 고려한 Web Service 구조

- React SPA와 FastAPI API를 분리합니다.
- `X-Request-ID`를 요청과 응답에 전달해 로그 추적을 돕습니다.
- `/health` 엔드포인트를 통해 서비스 생존 상태를 확인합니다.

---

## 법률 상담은 어떻게 동작하나요?

```text
사용자 질문
    ↓
FastAPI Chat API → 대화 메시지 저장
    ↓
질문 임베딩 → Pinecone에서 법령 청크 검색
    ↓
REF 번호가 부여된 근거 문서 구성
    ↓
LLM 답변 생성 → ⟦n⟧ 인용 앵커 포함
    ↓
답변과 sources 반환 → 메시지 저장 → Frontend 표시
```

검색 문서는 먼저 중복 제거한 뒤 번호를 부여합니다. 따라서 LLM의 인용 번호와 API의 출처 배열 번호가 일치합니다.

---

## 구성

```text
사용자 브라우저
    ├─ React / Vite Frontend
    │      └─ /api/* 요청
    └─ CloudFront → S3 정적 파일

FastAPI Backend
    ├─ Chat / History / Health Router
    ├─ RAG Service / OpenAI / Pinecone
    └─ SQLAlchemy / Alembic → SQLite 또는 PostgreSQL
```

| API | 설명 |
|---|---|
| `POST /api/chat/{session_id}` | 질문을 받아 답변과 `sources` 반환 |
| `GET /api/conversations/{session_id}/messages` | 세션의 메시지 조회 |
| `POST /api/conversations/{session_id}/messages` | 세션에 메시지 저장 |
| `GET /health` | 서비스 생존 확인 |

## 배포

문서와 Workflow에 기록된 배포 구성은 정적 Frontend를 S3와 CloudFront로 제공하고, Backend를 Elastic Beanstalk와 ALB로 운영하는 방식입니다. AWS OIDC를 사용해 장기 Access Key를 Workflow에 저장하지 않습니다.

현재 실제 운영 도메인과 배포 상태는 저장소 문서만으로 확인하지 않았습니다. 배포 절차는 [배포와 CI CD](https://github.com/youneedpython/chatbot-law-production/wiki/배포와-CI-CD)를 참고합니다.

## 기술 스택

| 영역 | 기술 |
|---|---|
| Frontend | React 19, Vite 7, React Router 7, React Markdown 10 |
| Backend | Python 3.11, FastAPI 0.124, Uvicorn |
| RAG | LangChain 1.2, OpenAI, Pinecone |
| Database | SQLAlchemy 2.0, Alembic, SQLite(Local) / PostgreSQL |
| 운영 | GitHub Actions(OIDC), Elastic Beanstalk, S3, CloudFront |

정확한 Version은 `backend/requirements.txt`와 `frontend/package.json`을 따릅니다.

## 품질 검증

- Pull Request에서 Backend `pytest`와 Frontend `npm run build`를 경로별로 실행합니다.
- Backend Test는 `backend/tests/test_smoke.py`의 Smoke Test 하나입니다.
- 검증 범위의 한계는 [Roadmap과 한계](https://github.com/youneedpython/chatbot-law-production/wiki/Roadmap과-한계)에 적었습니다.

---

## 시작하기

Python `3.11`, Node.js `20.19` 이상, OpenAI / Pinecone API Key가 필요합니다.

```bash
# 1. Backend (http://localhost:8000)
cd backend
cp .env.example .env                      # API Key, Pinecone Namespace, 임베딩 모델 입력 (Wiki 참고)
python -m venv venv && source venv/Scripts/activate
pip install -r requirements.txt
python -m app.init_db                     # SQLite에 Table 생성
uvicorn app.main:app --reload --port 8000

# 2. Frontend (http://localhost:5173, 별도 터미널)
cd frontend
echo "VITE_API_BASE_URL=/api" > .env
npm ci
npm run dev
```

운영체제별 명령, 환경변수 전체 목록, 자주 만나는 문제는 [Local 실행](https://github.com/youneedpython/chatbot-law-production/wiki/Local-실행)과 [환경 변수](https://github.com/youneedpython/chatbot-law-production/wiki/환경-변수)에 있습니다.

---

## 프로젝트 구조

```text
chatbot-law-production/
├── backend/                 # FastAPI API, RAG, DB, 인덱싱 파이프라인
│   ├── app/                 # Router, Service, Model, Schema
│   ├── alembic/             # DB Migration
│   ├── data/                # 법령 원문과 인덱스 메타데이터
│   ├── scripts/indexing/    # DOCX 로드·청킹·임베딩·Pinecone 적재
│   └── tests/               # Backend Test
├── frontend/                # React / Vite SPA
├── docs/images/             # 저장소에 포함된 서비스 화면
├── .github/workflows/       # CI와 배포 Workflow
└── CHANGELOG.md             # Release별 변경 기록
```
