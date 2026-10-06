# Chatbot Law Production

**전세사기 피해자를 위한 법률·행정 절차 안내 AI 서비스입니다.**

사용자가 질문을 입력하면 관련 법령 문서를 검색하고, 근거가 확인된 절차와 기관 정보를 대화형 답변으로 제공합니다. 답변에는 검색된 법령 조항을 가리키는 인용 정보가 함께 반환됩니다.

![상담 초기 화면](docs/images/service_preview_blank.png)

> 이 서비스는 공인된 법률 자문이나 법적 대리 행위를 제공하지 않습니다. 실제 사건은 대한법률구조공단, 전세피해지원센터 또는 전문 변호사와 상담해야 합니다.

| | 내용 |
|---|---|
| 화면 | React SPA 기반 상담 화면과 세션별 대화 이력 |
| 데이터 | 전세사기피해자 지원 특별법 및 주택임대차보호법 원문 |
| 모델 | OpenAI LLM / `text-embedding-3-small` 임베딩 |
| 검색 | Pinecone Vector Store, 기본 `RAG_TOP_K=5` |
| 배포 | S3 · CloudFront · Elastic Beanstalk · RDS PostgreSQL |

**더 읽기**: [Wiki](https://github.com/youneedpython/chatbot-law-production/wiki) · [Releases](https://github.com/youneedpython/chatbot-law-production/releases) · [CHANGELOG.md](CHANGELOG.md)

---

## 사용 결과

![법률 상담 답변 화면](docs/images/service_preview_chat.png)

상담 답변은 번호 목록을 기본 형식으로 사용하며, 법령 근거가 부족한 내용은 추측하지 않도록 구성되어 있습니다.

---

## 주요 기능

### 1. 법률 문서 기반 RAG

- 법령을 법률명·조문·항 단위 메타데이터와 함께 검색합니다.
- 검색된 근거를 바탕으로 답변하며, 근거가 부족한 법률 판단은 생성하지 않습니다.
- 법률 원문은 `backend/data/raw_docs/`에 저장된 문서를 인덱싱한 결과를 사용합니다.

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

| 영역 | 구성 | 역할 |
|---|---|---|
| Frontend | React 18, Vite, React Markdown | 상담 화면과 인용 표시 |
| Backend | Python 3.11, FastAPI, Uvicorn | API와 세션 처리 |
| RAG | LangChain, OpenAI, Pinecone | 임베딩·검색·답변 생성 |
| Database | SQLAlchemy, Alembic, SQLite / PostgreSQL | 세션과 메시지 저장 |
| 운영 | GitHub Actions, Elastic Beanstalk, S3, CloudFront | Build와 배포 |

---

## 배포

문서와 Workflow에 기록된 배포 구성은 정적 Frontend를 S3와 CloudFront로 제공하고, Backend를 Elastic Beanstalk와 ALB로 운영하는 방식입니다. AWS OIDC를 사용해 장기 Access Key를 Workflow에 저장하지 않습니다.

현재 실제 운영 도메인과 배포 상태는 저장소 문서만으로 확인하지 않았습니다. 배포 절차는 [배포와 CI CD](https://github.com/youneedpython/chatbot-law-production/wiki/배포와-CI-CD)를 참고합니다.

---

## 품질 검증

- Pull Request에서 Backend `pytest`와 Frontend `npm run build`를 경로별로 실행합니다.
- Backend 기본 테스트는 `backend/tests/test_smoke.py`에 있습니다.
- Local 검증 절차는 [Local 실행](https://github.com/youneedpython/chatbot-law-production/wiki/Local-실행)에 정리되어 있습니다.

---

## 시작하기

1. Python `3.11.x`, Node.js `18.x` 또는 `20.x` 이상, Git을 준비합니다.
2. `backend/.env.example`을 `backend/.env`으로 복사하고 `OPENAI_API_KEY`를 설정합니다.
3. Backend에서 의존성을 설치하고 Alembic을 실행합니다.

```bash
cd backend
python -m venv venv
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

4. 별도 터미널에서 Frontend를 실행합니다.

```bash
cd frontend
npm ci
npm run dev
```

5. `http://localhost:8000/health`와 `http://localhost:5173`에서 실행 결과를 확인합니다.

환경 변수와 문제 해결 방법은 [Local 실행](https://github.com/youneedpython/chatbot-law-production/wiki/Local-실행)과 [환경 변수](https://github.com/youneedpython/chatbot-law-production/wiki/환경-변수)를 참고합니다.

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
