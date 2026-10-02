# ⚙️ 환경 변수 가이드 (Environment Variables)

본 문서는 **Chatbot Law** 서비스의 백엔드, 프론트엔드 및 CI/CD 배포 파이프라인에서 사용하는 모든 환경 변수와 보안 시크릿 목록 및 설정 방법을 안내합니다.

---

## 🛡️ 환경 변수 관리 원칙

1. **단일 진입점 검증 (Fail-Fast)**
   - 백엔드는 애플리케이션 시작 시 `app/core/config.py`의 `validate_runtime_env()`를 통해 필수 환경 변수를 검증합니다.
   - 필수 변수(예: `OPENAI_API_KEY`)가 누락되면 런타임 오류를 방지하기 위해 서버 구동 즉시 프로세스가 종료됩니다.
2. **비밀키 저장소 분리**
   - 로컬 개발 환경: git 추적에서 제외된 `.env` 파일 사용
   - 운영 환경(AWS): AWS Elastic Beanstalk 환경 속성(Software Configuration) 및 GitHub Secrets/Variables 사용
   - **코드베이스 내 비밀키 및 토큰 하드코딩 절대 금지**

---

## 🐍 1. 백엔드 (Backend) 환경 변수

| 변수명 | 필수 여부 | 기본값 | 설명 및 예시 |
|:---|:---:|:---|:---|
| `ENV` | 선택 | `local` | 실행 환경 구분 (`local`, `dev`, `prod`). `local`일 때만 `.env` 파일을 로드함 |
| `OPENAI_API_KEY` | **필수** | - | OpenAI API 인증 키 (`sk-proj-...`) |
| `OPENAI_MODEL` | 선택 | `gpt-4o-mini` | 대화 답변 생성에 사용할 LLM 모델명 |
| `OPENAI_EMBEDDING_MODEL` | 선택 | `text-embedding-3-small` | RAG 문서 임베딩에 사용되는 벡터 임베딩 모델명 |
| `PINECONE_API_KEY` | 선택 (RAG 연동 시 필수) | - | Pinecone 벡터 데이터베이스 API 키 |
| `PINECONE_INDEX_NAME` | 선택 | `chatbot-law-dev` | 대상 Pinecone 인덱스 명칭 |
| `PINECONE_NAMESPACE` | 선택 | `""` (공백) | Pinecone 인덱스 내 네임스페이스 분리용 문자열 |
| `RAG_TOP_K` | 선택 | `5` | RAG 질의 시 검색해올 상위 관련 법령 청크 개수 |
| `DATABASE_URL` | 선택 | `sqlite:///./dev.db` | 데이터베이스 연결 문자열.<br>• 로컬: `sqlite:///./dev.db`<br>• 운영(RDS): `postgresql+psycopg2://user:pass@host:5432/dbname` |
| `LANGCHAIN_TRACING_V2` | 선택 | `false` | LangSmith 트레이싱 활성화 여부 (`true` 또는 `false`) |
| `LANGSMITH_API_KEY` | 선택 | - | LangSmith 프로젝트 추적용 API 키 |
| `LANGCHAIN_PROJECT` | 선택 | `chatbot-law-Prod` | LangSmith 대시보드 프로젝트 식별자 |

---

## ⚛️ 2. 프론트엔드 (Frontend - Vite) 환경 변수

프론트엔드는 빌드 타임에 Vite 환경 변수를 주입받습니다 (`import.meta.env`).

| 변수명 | 기본값 | 설명 |
|:---|:---|:---|
| `VITE_API_BASE_URL` | `/api` | 백엔드 API 기본 경로 (로컬 프록시 및 프로덕션 CloudFront 라우팅 규격) |
| `VITE_APP_ENV` | `dev` | 빌드 환경 식별자 (`dev` 또는 `prod`) |

---

## ☁️ 3. CI/CD 및 AWS 인프라 시크릿 (GitHub Secrets & Variables)

GitHub Actions 워크플로우(`.github/workflows/`)에서 AWS 리소스에 무중단 배포하기 위해 등록된 설정입니다.

### GitHub Secrets (보안 암호)
| 시크릿명 | 설명 | 사용처 |
|:---|:---|:---|
| `AWS_ROLE_ARN` | AWS OIDC 연동을 위한 IAM Role ARN (장기 Access Key 미사용) | Frontend / Backend 배포 |
| `AWS_REGION` | 배포 리전 (예: `ap-northeast-2`) | Frontend / Backend 배포 |
| `EB_APP_NAME` | AWS Elastic Beanstalk 애플리케이션 명칭 | Backend EB 배포 |
| `EB_ENV_NAME` | AWS Elastic Beanstalk 환경 명칭 (예: `Chatbotlawprod-env`) | Backend EB 배포 |
| `S3_BUCKET` | 백엔드 배포 아티팩트(ZIP 번들) 저장용 S3 버킷 | Backend EB 배포 |
| `FRONT_S3_BUCKET` | 프론트엔드 정적 파일 호스팅용 S3 버킷 | Frontend 배포 |
| `CLOUDFRONT_DISTRIBUTION_ID` | 캐시 무효화(`create-invalidation`) 대상 CloudFront 배포 ID | Frontend 배포 |

### GitHub Variables (일반 변수)
| 변수명 | 값 | 설명 |
|:---|:---|:---|
| `VITE_API_BASE_URL` | `/api` | 프론트엔드 빌드 시 주입되는 API 베이스 경로 |
| `VITE_APP_ENV` | `prod` | 운영 환경 빌드 플래그 |

---

## 📝 `.env` 설정 예시 파일

로컬 개발 시 `backend/.env`를 아래와 같이 구성하여 사용합니다:

```env
## Environment type (local | dev | prod)
ENV=local

## OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

## Pinecone Vector DB
PINECONE_API_KEY=pcsk_xxxxxxxxxxxxxxxxxxxxxx
PINECONE_INDEX_NAME=chatbot-law-dev
RAG_TOP_K=5

## Database (Local SQLite)
DATABASE_URL=sqlite:///./dev.db

## LangSmith Observability
LANGCHAIN_TRACING_V2=false
LANGSMITH_API_KEY=
LANGCHAIN_PROJECT=chatbot-law-Prod
```
