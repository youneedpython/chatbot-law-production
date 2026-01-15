from dataclasses import dataclass
import os
from dotenv import load_dotenv


# ======================================
# Environment configuration
# ======================================
# 로컬 개발: .env가 존재하면 로드 (prod/eb에서는 보통 .env 없음)
load_dotenv()

def _as_bool(v: str | None) -> bool:
    if v is None:
        return False
    return v.strip().lower() in ("1", "true", "yes", "y", "on")


@dataclass(frozen=True)
class Settings:
    # Paths
    raw_docs_dir: str = os.getenv("RAW_DOCS_DIR", "data/raw_docs")
    manifest_path: str = os.getenv("INDEX_MANIFEST_PATH", "data/index_manifest.json")

    # OpenAI embeddings
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    # Pinecone
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "")
    pinecone_namespace: str = os.getenv("PINECONE_NAMESPACE", "default")

    # Chunking
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "120"))

    # Upsert batch size (Pinecone)
    upsert_batch_size: int = int(os.getenv("UPSERT_BATCH_SIZE", "50"))

    # Store text inside metadata (RAG retrieval 편의)
    store_text_in_metadata: bool = os.getenv("STORE_TEXT_IN_METADATA", "true").lower() == "true"

    # Safety
    fail_on_missing_env: bool = os.getenv("FAIL_ON_MISSING_ENV", "true").lower() == "true"

    # Dry run
    dry_run: bool = _as_bool(os.getenv("DRY_RUN"))
    save_manifest_on_dry_run: bool = os.getenv("SAVE_MANIFEST_ON_DRY_RUN", "true").lower() == "true"


def load_settings() -> Settings:
    s = Settings()
    if s.fail_on_missing_env and not s.pinecone_index_name:
        raise ValueError("PINECONE_INDEX_NAME is required.")
    return s
