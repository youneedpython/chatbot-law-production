# Changelog

All notable changes to this project are documented in this file.

---

## v0.4.2 — Production Observability & Deployment

### Added
- Request ID propagation via `X-Request-ID` header
- Automatic request_id generation and injection into responses
- Structured logging with request-level correlation
- Separate liveness and readiness health check endpoints
- Elastic Beanstalk deployment (production-ready backend)
- Environment-based configuration (dev / prod)

### Changed
- Refactored middleware and logging pipeline for observability
- Improved error handling for API and LLM layers
- Updated frontend API strategy to support proxy-based development and production deployment

### Notes
- Backend is now production-deployable
- Frontend deployment via S3 + CloudFront planned next

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
