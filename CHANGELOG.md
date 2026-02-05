# Changelog

All notable changes to this project are documented in this file.  
This project follows **Semantic Versioning** (`MAJOR.MINOR.PATCH`).



---

## v0.5.1 — Chat 입력 UI/UX 고도화 및 시각적 안정화
> Release Date: 2026-02-05

### ✨ 개요
v0.5.1 릴리스는 v0.5.0 이후 사용자 경험 개선을 목적으로 한  
프론트엔드 UI/UX 중심의 패치 릴리스입니다.

사용자 입력 흐름, 버튼 상태 표현, 아바타 시각 요소를 정비하여  
실제 상담 서비스 환경에서의 사용성과 신뢰도를 강화했습니다.

---

### 🚀 주요 변경 사항

#### Frontend — Chat UI/UX 개선
- 채팅 입력 영역을 단일 Dock 형태 UI로 재구성
- 아이콘 버튼 기반 입력 구조 도입
- 입력 가능/비활성/전송 조건에 따른 버튼 상태 표현 명확화
- Enter 전송 / Shift+Enter 줄바꿈 UX 정리

#### Frontend — 시각 요소 개선
- 채팅 아바타 디자인 업데이트 (정의의 저울 심볼 적용)
- 아바타 이미지 용량 최적화 및 렌더링 성능 개선

---

### 영향 범위
- Backend / RAG / Indexing 로직 변경 없음
- 기존 기능 동작 변경 없음


---

## v0.5.0 — RAG 안정화 및 Chat UI/UX 개선

### ✨ 개요
v0.5.0 릴리스는 전세사기 피해자 법률 상담 챗봇의  
RAG 파이프라인 안정화와 채팅 UI/UX 개선을 포함한 통합 릴리스입니다.

검색 정확도, citation 렌더링, 사용자 입력 경험을 전반적으로 개선하여  
실서비스 운영을 위한 품질 기준을 한 단계 끌어올렸습니다.

---

### 🚀 주요 변경 사항

#### Backend — RAG 파이프라인 안정화
- Pinecone 기반 검색/응답 흐름 안정화
- top_k 설정 및 타임아웃 처리 개선
- 메타데이터 sanitize 및 법령 citation 정확성 개선
- citation marker 구조 개선 및 프론트 렌더링 정렬

#### Indexing — 운영 스크립트 정비
- Pinecone 인덱싱 파이프라인 스크립트 정리
- index manifest 스냅샷 관리 구조 도입
- metadata backfill 흐름 안정화

#### Frontend — Chat UI/UX 개선
- ChatGPT 스타일에 가까운 채팅 레이아웃 개선
- 법 조문 기반 citation 자연스러운 렌더링
- Suggestion chips 추가 및 클릭 전송 UX 적용
- 채팅 입력 UX 개선 (Enter 전송 / Shift+Enter 줄바꿈)
- 아바타 UI 개선 및 이미지 최적화

---

### 비고
- 본 릴리스는 기능 추가와 안정화를 함께 포함한 메이저 마이너 릴리스입니다.
- 본 릴리스는 이후 UI/UX 고도화 및 streaming RAG 기능 확장을 위한
  기술적 기준선(baseline)을 확립한 릴리스입니다.


---

## v0.4.4 — Frontend CI/CD Pipeline for Production Deployment
> Release Date: 2026-01-XX

### ✨ 개요
v0.4.4 릴리스는 프론트엔드 애플리케이션의  
CI/CD 파이프라인을 구축하고,  
S3 + CloudFront 기반의 프로덕션 배포 자동화를 완료한 릴리스입니다.

기존 v0.4.3에서 백엔드 CI/CD 안정화를 완료한 이후,  
본 릴리스를 통해 프론트엔드 또한 독립적인 배포 파이프라인을 갖추며  
서비스 전체 배포 흐름이 완성되었습니다.

---

### 🚀 주요 변경 사항

#### 1. Frontend CI/CD 파이프라인 구축
- GitHub Actions 기반 프론트엔드 배포 워크플로우 추가
- `frontend-dev`, `frontend-prod` 환경 분리 구성
- GitHub Environments 기반 Secrets / Variables 관리 체계 도입

#### 2. AWS 배포 자동화
- OIDC 기반 IAM Role Assume 방식 적용
- S3 정적 파일 배포 자동화
- CloudFront 캐시 무효화(Invalidation) 자동 실행

#### 3. 운영 및 배포 구조 개선
- Backend / Frontend CI/CD 파이프라인 완전 분리
- 배포 책임 범위 명확화 (Backend ↔ Frontend)
- main 브랜치 기준 Production 배포 일관성 확보

---

### ✅ 배포 및 검증
- 배포 대상: Frontend (Vite, S3, CloudFront)
- 배포 상태: Production 배포 완료
- 검증 항목:
  - GitHub Actions Workflow 정상 수행
  - S3 정적 리소스 업로드 확인
  - CloudFront 캐시 무효화 정상 동작
  - 서비스 접근 및 렌더링 정상 확인

---

### 📝 비고
- 본 릴리스는 프론트엔드 CI/CD 파이프라인 완성을 기준으로 한 릴리스입니다.
- 이후 릴리스부터는 Vector DB(RAG) 등 핵심 기능 구현 중심으로 진행될 예정입니다.


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
