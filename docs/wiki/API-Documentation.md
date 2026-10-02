# 📡 API 명세서 (API Documentation)

본 문서는 **Chatbot Law – Production** 백엔드가 제공하는 RESTful API 엔드포인트 명세, 요청/응답 형식, 그리고 전역 요청 추적(`X-Request-ID`) 규격을 설명합니다.

---

## 🌐 기본 접속 정보 (Base URL)

- **로컬 개발**: `http://localhost:8000`
- **프로덕션 (ALB / CloudFront)**: `https://<배포도메인>` (API 접두사: `/api`)
- **대화형 Swagger UI**: `/docs`
- **ReDoc 문서**: `/redoc`
- **OpenAPI Schema (JSON)**: `/openapi.json`

---

## 🔍 전역 요청 추적 (`X-Request-ID`)

분산 환경에서의 장애 추적성과 관측 가능성(Observability)을 위해 모든 HTTP 요청/응답에 `X-Request-ID` 헤더가 연동됩니다.

1. **클라이언트 제공**: 클라이언트가 요청 헤더에 `X-Request-ID`를 전달하면 해당 ID를 로그와 응답 헤더에 그대로 유지합니다.
2. **서버 자동 발급**: 헤더가 생략된 경우 FastAPI 미들웨어(`app/core/request_id.py`)에서 UUID v4를 자동 발급합니다.
3. **응답 헤더 반영**: 모든 HTTP 응답 헤더에 `X-Request-ID`가 포함되어 반환됩니다.

---

## 📋 엔드포인트 요약

| Method | Path | 태그 | 설명 |
|:---:|:---|:---:|:---|
| `GET` | `/health` | Health | 서비스 생존 상태 확인 (ALB 헬스체크용) |
| `POST` | `/api/chat/{session_id}` | Chat | RAG 기반 질의응답 생성 및 대화 저장 |
| `GET` | `/api/conversations/{session_id}/messages` | History | 세션별 메시지 이력 페이징 조회 |
| `POST` | `/api/conversations/{session_id}/messages` | History | 세션에 메시지 단건 추가 |

---

## 1. 헬스체크 (Health Check)

서비스 프로세스가 정상적으로 요청을 수신할 수 있는지 확인합니다. AWS ALB 및 CloudFront 라우팅 유효성 검증에 사용됩니다.

### `GET /health`

#### 요청 헤더
- 없음

#### 응답 예시 (`200 OK`)
```json
{
  "status": "ok",
  "service": "chatbot-law-prod"
}
```

---

## 2. 챗봇 상담 질의응답 (RAG Chat)

사용자 질의를 수신하여 법률 벡터 검색(Pinecone)을 수행하고, 법령 근거 기반의 답변을 생성합니다. 사용자와 어시스턴트 메시지는 DB에 자동으로 영속화됩니다.

### `POST /api/chat/{session_id}`

#### 경로 파라미터 (Path Parameters)
- `session_id` (string, 필수): 대화 세션 고유 식별자 (예: UUID)

#### 요청 헤더
- `Content-Type: application/json`
- `X-Request-ID` (string, 선택): 추적용 고유 요청 ID

#### 요청 본문 (Request Body)
```json
{
  "message": "전세사기 피해자로 인정받으려면 어떤 요건이 필요한가요?"
}
```

#### 응답 본문 (`200 OK`)
```json
{
  "answer": "전세사기피해자 지원 및 주거안정에 관한 특별법 제3조에 따라 다음 요건을 모두 갖추어야 합니다:\n\n1. 주택의 인도와 주민등록(전입신고)을 마치고 확정일자를 갖춘 경우 ⟦1⟧\n2. 임대차보증금이 3억원 이하인 경우 (위원회 결정에 따라 5억원까지 상향 가능) ⟦1⟧\n3. 임대인의 파산, 회생, 경매 절차가 개시되었거나 보증금 미반환이 발생한 경우 ⟦1⟧\n4. 임대인에 대한 수사 개시 등 다수의 임차인에게 피해가 발생할 우려가 있는 경우 ⟦1⟧",
  "session_id": "c88f117a-5df9-4ad3-9e5c-097c36a6cf49",
  "sources": [
    {
      "law_title": "전세사기피해자 지원 및 주거안정에 관한 특별법",
      "article_no": 3,
      "article_title": "전세사기피해자등의 결정",
      "clause_no": 1,
      "text": "제3조(전세사기피해자등의 결정) ① 국토교통부장관은 다음 각 호의 요건을 모두 갖춘 임차인을 전세사기피해자로 결정한다...",
      "source": "law_1.docx"
    }
  ]
}
```

#### 상태 코드
- `200 OK`: 질의응답 및 DB 저장 성공
- `400 Bad Request`: `message` 필드가 비어있거나 공백인 경우

---

## 3. 대화 이력 조회 (Get Messages)

특정 대화 세션에 저장된 이전 대화 목록을 순서대로 조회합니다.

### `GET /api/conversations/{session_id}/messages`

#### 경로 파라미터 (Path Parameters)
- `session_id` (string, 필수): 대화 세션 ID

#### 쿼리 파라미터 (Query Parameters)
- `limit` (integer, 선택, 기본값 `50`, 최소 `1`, 최대 `100`): 한 번에 조회할 메시지 수
- `before_seq` (integer, 선택): 이전 메시지 페이징을 위한 기준 `seq` 번호

#### 응답 본문 (`200 OK`)
```json
{
  "conversation_id": "c88f117a-5df9-4ad3-9e5c-097c36a6cf49",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "전세사기 피해자 지원 대상 요건이 어떻게 되나요?",
      "seq": 1,
      "created_at": "2026-10-02T06:30:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "전세사기피해자로 결정받기 위해서는 다음의 요건을... ⟦1⟧",
      "seq": 2,
      "created_at": "2026-10-02T06:30:03Z"
    }
  ],
  "has_more": false
}
```

---

## 4. 메시지 단건 추가 (Append Message)

특정 세션에 사용자의 추가 메모나 시스템 안내 메시지를 수동으로 추가할 때 사용합니다.

### `POST /api/conversations/{session_id}/messages`

#### 요청 본문 (Request Body)
```json
{
  "role": "user",
  "content": "확인 감사드립니다."
}
```

#### 응답 본문 (`200 OK`)
```json
{
  "id": 3,
  "conversation_id": "c88f117a-5df9-4ad3-9e5c-097c36a6cf49",
  "role": "user",
  "content": "확인 감사드립니다.",
  "seq": 3,
  "created_at": "2026-10-02T06:32:15Z"
}
```

---

## 💻 cURL 호출 테스트 예시

### 1) 헬스체크
```bash
curl -X GET http://localhost:8000/health
```

### 2) X-Request-ID를 포함한 RAG 질의
```bash
curl -X POST http://localhost:8000/api/chat/session-test-001 \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: debug-trace-12345" \
  -d '{"message":"보증금을 돌려받기 위한 우선변제권 요건은?"}'
```
