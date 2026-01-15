import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

from .settings import load_settings
from .logger import get_logger
from .manifest import load_manifest, save_manifest
from .loader_docx import load_docx, blocks_to_text
from .cleaner import light_clean
from .chunker import chunk_text
from .embedder import Embedder
from .pinecone_store import PineconeStore

log = get_logger("indexing.pipeline")

def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def build_vector_id(source: str, doc_sha: str, chunk_index: int) -> str:
    """
    안정적 ID:
    - 같은 파일 내용(doc_sha)이면 chunk_index 기반으로 항상 동일
    - 파일 내용이 바뀌면 doc_sha가 바뀌므로 ID도 바뀜
    """
    return f"{source}::{doc_sha[:12]}::{chunk_index}"

def process_one_doc(
    *,
    doc_path: Path,
    store: PineconeStore,
    embedder: Embedder,
    settings,
    manifest: Dict[str, Any],
) -> None:
    filename = doc_path.name
    doc_sha = file_sha256(doc_path)

    prev = manifest.get(filename)
    if prev and prev.get("sha256") == doc_sha:
        log.info(f"SKIP unchanged: {filename}")
        return

    # 변경된 문서면 기존 벡터 삭제(중복/잔존 방지)
    if prev:
        if settings.dry_run:
            log.info(f"DRY_RUN=true -> skip delete_by_source: {filename}")
        else:
            log.info(f"DELETE old vectors by source: {filename}")
            store.delete_by_source(filename)

    log.info(f"LOAD: {filename}")
    blocks = load_docx(str(doc_path))
    text = blocks_to_text(blocks)
    text = light_clean(text)

    chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        log.warning(f"NO CHUNKS: {filename} (empty after processing)")
        return

    # 임베딩 배치 생성
    log.info(f"EMBED: {filename} chunks={len(chunks)}")
    embeddings = embedder.embed_documents(chunks)

    # Pinecone upsert batch
    vectors: List[Dict[str, Any]] = []
    for i, (chunk, vec) in enumerate(zip(chunks, embeddings)):
        metadata = {
            "source": filename,           # delete/filter 핵심 키
            "doc_sha": doc_sha,           # 버전 추적
            "chunk_index": i,
            "doc_type": "law_docx",
            "indexed_at": utc_now_iso(),
        }
        if settings.store_text_in_metadata:
            metadata["text"] = chunk

        vectors.append({
            "id": build_vector_id(filename, doc_sha, i),
            "values": vec,
            "metadata": metadata,
        })

        if len(vectors) >= settings.upsert_batch_size:
            if settings.dry_run:
                log.info(f"DRY_RUN=true -> skip upsert batch ({len(vectors)}) for {filename}")
            else:
                store.upsert(vectors)
            vectors.clear()

    if vectors:
        if settings.dry_run:
            log.info(f"DRY_RUN=true -> skip final upsert ({len(vectors)}) for {filename}")
        else:
            store.upsert(vectors)

    # manifest 갱신
    manifest[filename] = {
        "sha256": doc_sha,
        "indexed_at": utc_now_iso(),
        "chunks": len(chunks),
    }
    log.info(f"DONE: {filename} (sha={doc_sha[:12]})")

def main() -> None:
    settings = load_settings()

    raw_dir = Path(settings.raw_docs_dir)
    if not raw_dir.exists():
        raise FileNotFoundError(f"RAW_DOCS_DIR not found: {raw_dir}")

    manifest = load_manifest(settings.manifest_path)

    store = PineconeStore(
        index_name=settings.pinecone_index_name,
        namespace=settings.pinecone_namespace,
    )
    embedder = Embedder(model=settings.openai_embedding_model)

    doc_paths = sorted(raw_dir.glob("*.docx"))
    log.info(f"FOUND DOCX: {len(doc_paths)} in {raw_dir}")

    if settings.dry_run:
        log.info("DRY_RUN=true -> will NOT write to Pinecone (no delete/upsert).")

    for p in doc_paths:
        try:
            process_one_doc(
                doc_path=p,
                store=store,
                embedder=embedder,
                settings=settings,
                manifest=manifest,
            )
        except Exception as e:
            # 운영에서는 한 파일 실패로 전체 중단하지 않게(원하면 fail-fast로 바꿀 수 있음)
            log.exception(f"FAILED: {p.name} error={e}")

    if settings.dry_run and not settings.save_manifest_on_dry_run:
        log.info("DRY_RUN=true & SAVE_MANIFEST_ON_DRY_RUN=false -> skip manifest save.")
    else:
        save_manifest(settings.manifest_path, manifest)
        log.info(f"MANIFEST SAVED: {settings.manifest_path}")

    log.info("✅ Indexing pipeline completed.")
