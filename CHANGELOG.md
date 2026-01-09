# Changelog

All notable changes to this project are documented in this file.  
This project follows **Semantic Versioning** (`MAJOR.MINOR.PATCH`).

---

## v0.4.3 — CI/CD 안정화 및 프로덕션 릴리즈 정렬

> **상태**: Stable / Production-ready  
> **릴리즈 범위**: Backend (FastAPI, Elastic Beanstalk)

### ✅ 검증 요약
- 백엔드 프로덕션 환경 배포 완료
- CI/CD 단계에서 런타임 환경 변수에 의존하지 않도록 구조 개선 확인
- 운영 환경에서 애플리케이션 정상 기동 확인
- `/health`, `/docs` 엔드포인트 정상 응답 확인

---

### 변경 사항

#### CI/CD 구조 안정화
- CD 단계에서 Alembic 마이그레이션 실행 제거
- 데이터베이스 마이그레이션과 애플리케이션 배포 책임 분리
- CI 단계에서 런타임 전용 환경 변수에 의존하던 구조 제거

#### 환경 변수 검증 방식 개선
- `OPENAI_API_KEY` 필수 여부 검증을 애플리케이션 실행 시점으로 이동
- import 시점 검증 로직을 명시적인 런타임 검증 함수로 분리
- CI 환경에서 필수 환경 변수가 없어 발생하던 실패 문제 해결

#### 릴리즈 및 배포 기준 정렬
- `main` 브랜치를 단일 프로덕션 기준 브랜치로 재정렬
- 태그(`v0.4.3`) 기반 릴리즈 기준점 명확화
- 빌드, 배포, 런타임 단계 간 역할 분리 명확화

---

### 인프라 / 배포
- Elastic Beanstalk (Production) 환경에 백엔드 배포 완료
- CI/CD 파이프라인 안정성 확보
- 본 릴리즈에서는 데이터베이스 스키마 변경 없음

---

### 비고
- 본 릴리즈는 **기능 추가보다는 운영 안정성과 배포 정합성 확보에 중점**을 둔 릴리즈입니다.
- 데이터베이스 마이그레이션은 CI/CD 파이프라인 외부에서 별도로 관리됩니다.
- 이후 프론트엔드 CI/CD 통합 및 자동화 작업을 위한 기반 릴리즈입니다.



---

## v0.4.2 — Production Deployment, DB Migration & Edge Integration

> **Status**: Stable / Production-ready  
> **Environment parity**: `dev` == `prod` (code & DB schema aligned)

### ✅ Verification Summary
- Production database migration **successfully applied**
  - `alembic current` → `c6973679b652 (head)`
  - `alembic heads` → `c6973679b652 (head)`
- No pending migrations detected
- PostgreSQL schema is identical across `dev` and `prod`

---

### Added
- **Request tracing & observability**
  - Request ID propagation via `X-Request-ID` header
  - Automatic request_id generation for inbound requests
  - Structured logging with request-level correlation

- **Health & operational endpoints**
  - Separate **liveness** and **readiness** health check endpoints
  - Public health exposure via CloudFront (`/health`)

- **Database & persistence**
  - PostgreSQL migration pipeline using **Alembic**
  - Finalized initial production schema
  - Transactional DDL support
  - Environment-aware migration context

- **Deployment & edge integration**
  - Elastic Beanstalk production backend (load-balanced)
  - CloudFront → ALB → EB routing configuration
  - Public API exposure via CloudFront behaviors
    - `/health`
    - `/docs` (Swagger UI)
    - `/openapi.json`


### Changed
- Refactored middleware pipeline for production observability
- Improved API and LLM-layer error handling
- Backend refactored to ensure **stateless request processing**
- Unified configuration strategy across dev / prod environments
- Improved CORS handling for CloudFront-originated traffic
- Hardened API error responses for production traffic
- Updated Elastic Beanstalk lifecycle hooks for stability

---

### Infrastructure / Deployment
- Backend deployed on **Elastic Beanstalk (Load Balanced Environment)**
- Database migrated from **SQLite → PostgreSQL**
- Frontend served via **S3 + CloudFront**
- Origin separation enforced:
  - Static assets → S3
  - Dynamic API → ALB / EB

---

### Notes
- CI/CD pipeline is **not yet implemented** (manual release process)
- This release establishes a **stable baseline** for future work:
  - CI/CD automation
  - RAG (Retrieval-Augmented Generation) integration
  - Authentication & rate limiting

---

## v0.4.1 — Logging & Health Foundations

### Added
- Centralized logger configuration
- Initial health check endpoint
- Environment variable standardization

### Changed
- Internal refactoring to prepare for observability
- Cleanup of legacy debug logs

---

## v0.4.0 — Backend History Architecture

### Added
- SQLite-based persistence for conversations and messages
- Session-based conversation model (conversation_id = session_id)
- History API to retrieve messages per session
- Database initialization script (`init_db`)

### Changed
- Shifted source of truth from frontend localStorage to backend database
- Refactored chat flow to explicitly orchestrate:
  - user message persistence
  - LLM invocation layer (stubbed)
  - assistant message persistence
- Improved API design for multi-device and session continuity

### Notes
- LLM call is stubbed for architecture validation
- Designed as a foundation for future RAG and contextual conversation support
