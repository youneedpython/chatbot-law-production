# 🔍 법률 데이터 인덱싱 파이프라인 (Data Indexing)

본 문서는 **전세사기 관련 법률 원문(DOCX) 데이터**를 전처리하고, 조·항·호 단위 메타데이터와 함께 임베딩하여 **Pinecone Vector Database**에 적재하는 파이프라인의 구조 및 실행 방법을 다룹니다.

---

## 🎯 인덱싱 파이프라인 설계 원칙

1. **도메인 특화 청킹 (Legal Structural Chunking)**
   - 일반 텍스트 분할기(RecursiveCharacterTextSplitter 등)는 법률 조항의 의미 단위를 훼손할 위험이 있습니다.
   - 본 시스템은 법률명, 조 번호(`article_no`), 조 제목(`article_title`), 항 번호(`clause_no`)를 보존하는 전용 청커(`chunker.py`)를 사용하여 인덱싱합니다.
2. **멱등성(Idempotency) 및 증분 인덱싱 (Incremental Indexing)**
   - 파일의 SHA-256 해시를 `index_manifest.json`에 기록하여 변경되지 않은 문서는 자동으로 건너뜁니다(`SKIP unchanged`).
   - 문서가 수정된 경우 구 버전 벡터를 소스 단위로 완전 삭제(`delete_by_source`)한 뒤 신규 벡터를 업서트하여 중복 데이터를 방지합니다.
3. **결정론적 벡터 ID (Deterministic Vector ID)**
   - `{filename}::{doc_sha[:12]}::{chunk_index}` 구조로 벡터 ID를 생성하여 재실행 시에도 일관된 식별자를 유지합니다.

---

## 📂 인덱싱 대상 데이터 및 모듈 구조

### 1) 대상 문서 (`backend/data/raw_docs/`)
- `law_1.docx`: **전세사기피해자 지원 및 주거안정에 관한 특별법**
- `law_2.docx`: **주택임대차보호법**

### 2) 파이프라인 모듈 (`backend/scripts/indexing/`)
| 모듈명 | 역할 |
|:---|:---|
| `loader_docx.py` | DOCX 문서 파싱 및 문단/표 블록 단위 텍스트 추출 |
| `cleaner.py` | 특수문자, 불필요한 줄바꿈 및 서식 태그 경량 정제 |
| `chunker.py` | 제N조(제목) 단위 및 항 번호를 감지하여 메타데이터와 함께 구조화 분할 |
| `embedder.py` | OpenAI `text-embedding-3-small` (1536차원) 배치 임베딩 생성 |
| `pinecone_store.py` | Pinecone 인덱스 연결, 네임스페이스 관리, Upsert 및 삭제 연산 |
| `manifest.py` | `backend/data/index_manifest.json` 해시 동기화 및 캐시 관리 |
| `pipeline.py` | 전체 인덱싱 흐름 오케스트레이션 |

---

## 🏷️ 벡터 메타데이터 스키마 (Metadata Schema)

Pinecone에 적재되는 각 벡터는 RAG 답변 생성 시 정확한 출처 표기를 위해 다음과 같은 메타데이터를 포함합니다:

```json
{
  "law_title": "전세사기피해자 지원 및 주거안정에 관한 특별법",
  "article_no": 3,
  "article_title": "전세사기피해자등의 결정",
  "clause_no": 1,
  "text": "제3조(전세사기피해자등의 결정) ① 국토교통부장관은 다음 각 호의 요건을 모두 갖춘 임차인을 전세사기피해자로 결정한다...",
  "source": "law_1.docx"
}
```

---

## 🚀 파이프라인 실행 방법

모든 명령어는 **`backend` 디렉터리**에서 실행합니다. 사전에 `.env`에 `OPENAI_API_KEY`와 `PINECONE_API_KEY`가 설정되어 있어야 합니다.

### 1) 기본 인덱싱 실행 (Upsert)
```bash
cd backend
python -m scripts.indexing
```

**정상 실행 로그 예시**:
```text
[INFO] indexing.pipeline - START indexing pipeline
[INFO] indexing.pipeline - Target files found: 2
[INFO] indexing.pipeline - LOAD: law_1.docx
[INFO] indexing.pipeline - Chunks generated: 48
[INFO] indexing.embedder - Generating embeddings for 48 chunks...
[INFO] indexing.pinecone - Upserted 48 vectors to Pinecone index 'chatbot-law-dev'
[INFO] indexing.pipeline - SKIP unchanged: law_2.docx
[INFO] indexing.pipeline - Manifest updated. Done!
```

### 2) 모의 실행 (Dry Run)
실제 Pinecone에 벡터를 업서트하거나 삭제하지 않고 파싱 및 청킹 결과만 검증할 때 사용합니다:
```bash
# Windows PowerShell
$env:DRY_RUN="true"
python -m scripts.indexing

# Bash / Linux
DRY_RUN=true python -m scripts.indexing
```

---

## 🔗 RAG 앙커 토큰 인용 연계 방식

1. 사용자가 질문을 입력하면 백엔드 `retriever_service.py`가 사용자 질의를 임베딩하여 Pinecone에서 관련 법령 청크 Top-K(기본 5개)를 검색합니다.
2. 검색된 문서들은 `[REF-1]`, `[REF-2]` 형태로 LLM 프롬프트 컨텍스트에 주입됩니다.
3. LLM은 답변 생성 시 인용 출처 뒤에 `⟦1⟧`, `⟦2⟧` 특수 앙커 토큰을 생성합니다.
4. 백엔드는 답변(`answer`)과 함께 `sources` 메타데이터 배열을 프론트엔드로 반환합니다.
5. 프론트엔드는 `⟦1⟧` 토큰을 실제 법률명과 조항명(예: `[전세사기피해자법 제3조]`) 뱃지 컴포넌트로 치환 렌더링합니다.
