# Changelog

All notable changes to this project are documented in this file.  
This project follows **Semantic Versioning** (`MAJOR.MINOR.PATCH`).

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
