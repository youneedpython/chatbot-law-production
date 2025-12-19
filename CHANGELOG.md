# Changelog

## v0.4.0 — Backend History Architecture

### Added
- SQLite-based persistence for conversations and messages
- Session-based conversation model (conversation_id = session_id)
- History API to retrieve messages per session
- Database initialization script (init_db)

### Changed
- Shifted source of truth from frontend localStorage to backend database
- Refactored chat flow to explicitly orchestrate:
  - user message persistence
  - LLM invocation layer (stubbed)
  - assistant message persistence
- Improved API design for multi-device and session continuity

### Notes
- LLM call is currently stubbed for architecture validation
- Designed as a foundation for future RAG and contextual conversation support
