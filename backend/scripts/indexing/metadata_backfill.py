import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from pinecone import Pinecone

# =========================================================
# Config
# =========================================================

@dataclass(frozen=True)
class BackfillSettings:
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "")
    pinecone_namespace: str = os.getenv("PINECONE_NAMESPACE", "law-docs")

    # index_manifest.json 위치 (루트에 두셨다면 기본값을 루트로)
    manifest_path: str = os.getenv("INDEX_MANIFEST_PATH", "index_manifest.json")

    # law_map.json 위치
    law_map_path: str = os.getenv("LAW_MAP_PATH", "scripts/indexing/law_map.json")

    # 배치 크기 (fetch/update)
    batch_size: int = int(os.getenv("PINECONE_BACKFILL_BATCH", "50"))

    # DRY_RUN=1 이면 실제 업데이트 하지 않음
    dry_run: bool = os.getenv("DRY_RUN", "").strip().lower() in ("1", "true", "yes", "y", "on")


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================================================
# Parsing: 조/항/호 추출
# =========================================================

# 예: "제10조(지원대상)" / "제 10 조 ( 지원대상 )" 등 허용
ARTICLE_RE = re.compile(r"제\s*(\d+)\s*조(?:\s*\(\s*([^)]+?)\s*\))?")
CLAUSE_RE  = re.compile(r"제\s*(\d+)\s*항")
ITEM_RE    = re.compile(r"제\s*(\d+)\s*호")

def parse_law_refs(text: str) -> Dict[str, Any]:
    """
    text에서 제n조/제n항/제n호를 '첫 매치' 기준으로 추출.
    v1 정책: first_match
    """
    result: Dict[str, Any] = {
        "article_no": None,
        "article_title": None,
        "clause_no": None,
        "item_no": None,
        "span_policy": "first_match",
    }

    if not text:
        return result

    m = ARTICLE_RE.search(text)
    if m:
        result["article_no"] = int(m.group(1))
        if m.group(2):
            result["article_title"] = m.group(2).strip()

    m = CLAUSE_RE.search(text)
    if m:
        result["clause_no"] = int(m.group(1))

    m = ITEM_RE.search(text)
    if m:
        result["item_no"] = int(m.group(1))

    return result


def build_citation(law_short: str, refs: Dict[str, Any]) -> str:
    """
    UI 표시용 citation 문자열 생성.
    예) "전세사기피해자법 시행령 제10조(지원대상) 제1항 제2호"
    """
    parts: List[str] = [law_short]

    article_no = refs.get("article_no")
    article_title = refs.get("article_title")
    clause_no = refs.get("clause_no")
    item_no = refs.get("item_no")

    if article_no is not None:
        if article_title:
            parts.append(f"제{article_no}조({article_title})")
        else:
            parts.append(f"제{article_no}조")

    if clause_no is not None:
        parts.append(f"제{clause_no}항")

    if item_no is not None:
        parts.append(f"제{item_no}호")

    # 조항 추출이 하나도 안 되면 법령명만 남게 되므로,
    # UI에서 의미가 약할 수 있어도 최소 표시값은 제공.
    return " ".join(parts)


# =========================================================
# Vector ID 규칙 (scripts/indexing/pipeline.py 규칙과 동일)
#   f"{source}::{doc_sha[:12]}::{chunk_index}"
# =========================================================
def build_vector_id(source: str, doc_sha: str, chunk_index: int) -> str:
    return f"{source}::{doc_sha[:12]}::{chunk_index}"


# =========================================================
# Pinecone IO
# =========================================================

def chunk_list(items: List[str], n: int) -> List[List[str]]:
    return [items[i:i+n] for i in range(0, len(items), n)]


def try_update_metadata(index, namespace: str, vec_id: str, new_meta: Dict[str, Any]) -> bool:
    """
    Pinecone client 버전에 따라 update API가 다를 수 있어
    가능한 형태를 순서대로 시도.
    성공하면 True, 실패하면 False 반환.
    """
    # 1) index.update(id=..., set_metadata=..., namespace=...)
    try:
        index.update(id=vec_id, set_metadata=new_meta, namespace=namespace)
        return True
    except TypeError:
        pass
    except Exception:
        # update 자체가 없거나, 권한/버전 이슈 등
        return False

    # 2) index.update(vector=..., namespace=...) 형태(구버전)
    try:
        index.update(vector={"id": vec_id, "set_metadata": new_meta}, namespace=namespace)
        return True
    except Exception:
        return False


# =========================================================
# Fetch 결과 정규화 (버전별 차이 처리)
# Helper for fetch_vectors_dict()
# =========================================================

def fetch_vectors_dict(fetched) -> Dict[str, Any]:
    """
    pinecone client 버전에 따라 fetch() 반환 타입이 다름(dict vs FetchResponse).
    이 함수를 통해 항상 dict 형태의 vectors 맵으로 정규화한다.

    반환: { "<vector_id>": { "id":..., "metadata":..., "values":... }, ... }
    """
    # 1) dict 형태(구버전)
    if isinstance(fetched, dict):
        return fetched.get("vectors", {}) or {}

    # 2) 객체 형태(신버전) - 보통 fetched.vectors 로 접근
    if hasattr(fetched, "vectors"):
        v = getattr(fetched, "vectors")
        # v가 이미 dict일 수도 있고, pydantic 모델/커스텀 타입일 수도 있음
        if isinstance(v, dict):
            return v
        # dict 변환 시도
        try:
            return dict(v)
        except Exception:
            pass

    # 3) 객체가 to_dict 제공하는 경우
    if hasattr(fetched, "to_dict"):
        try:
            d = fetched.to_dict()
            return d.get("vectors", {}) or {}
        except Exception:
            pass

    # 4) 최후: __dict__ 탐색
    try:
        d = fetched.__dict__
        if isinstance(d, dict):
            return d.get("vectors", {}) or {}
    except Exception:
        pass

    raise TypeError(f"Unsupported fetch response type: {type(fetched)}")


def as_dict(obj) -> Dict[str, Any]:
    """pinecone vector object/dict를 dict로 정규화"""
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "to_dict"):
        try:
            return obj.to_dict()
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        try:
            return dict(obj.__dict__)
        except Exception:
            pass
    # 마지막 fallback: mapping 캐스팅 시도
    try:
        return dict(obj)
    except Exception:
        raise TypeError(f"Cannot convert to dict: {type(obj)}")


def sanitize_pinecone_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pinecone metadata는 None(null) 허용하지 않음.
    허용 타입: string/number/boolean/list[string]
    => None 제거 + (필요시) 빈 문자열/잘못된 리스트 정리
    """
    clean: Dict[str, Any] = {}

    for k, v in (metadata or {}).items():
        if v is None:
            continue

        # bool 먼저 (bool은 int의 subclass)
        if isinstance(v, bool):
            clean[k] = v
            continue

        if isinstance(v, (int, float)):
            clean[k] = v
            continue

        if isinstance(v, str):
            vv = v.strip()
            if vv == "":
                continue
            clean[k] = vv
            continue

        if isinstance(v, list):
            # list[str]만 허용
            str_items = []
            for item in v:
                if item is None:
                    continue
                if isinstance(item, str):
                    s = item.strip()
                    if s:
                        str_items.append(s)
            if not str_items:
                continue
            clean[k] = str_items
            continue

        # dict/tuple/set 등은 Pinecone 메타데이터로 부적합 → 제거
        continue

    return clean



# =========================================================
# Main backfill logic
# =========================================================
def main() -> None:
    s = BackfillSettings()
    if not s.pinecone_index_name:
        raise ValueError("PINECONE_INDEX_NAME is required (env).")

    manifest = load_json(s.manifest_path)
    law_map = load_json(s.law_map_path)

    pc = Pinecone()
    index = pc.Index(s.pinecone_index_name)

    # (1) manifest 기반으로 모든 vector id 목록 생성
    all_ids: List[str] = []
    id_to_source: Dict[str, str] = {}

    for source, info in manifest.items():
        doc_sha = info.get("sha256") or info.get("sha") or ""
        chunks = int(info.get("chunks", 0))

        if not doc_sha or chunks <= 0:
            continue

        for i in range(chunks):
            vid = build_vector_id(source=source, doc_sha=doc_sha, chunk_index=i)
            all_ids.append(vid)
            id_to_source[vid] = source

    if not all_ids:
        print("[backfill] No vector ids generated from manifest.")
        return

    print(f"[backfill] index={s.pinecone_index_name}, namespace={s.pinecone_namespace}")
    print(f"[backfill] manifest={s.manifest_path}, law_map={s.law_map_path}")
    print(f"[backfill] total_ids={len(all_ids)}, batch_size={s.batch_size}, dry_run={s.dry_run}")

    updated = 0
    missing = 0

    for batch in chunk_list(all_ids, s.batch_size):
        # fetch existing vectors (values/metadata)
        fetched = index.fetch(ids=batch, namespace=s.pinecone_namespace)
        # vectors = fetched.get("vectors", {}) or {}
        vectors = fetch_vectors_dict(fetched)


        # update per vector
        for vid in batch:
            v_raw = vectors.get(vid)
            v = as_dict(v_raw)
            if not v:
                missing += 1
                continue

            meta: Dict[str, Any] = (v.get("metadata") or {}).copy()
            source = meta.get("source") or id_to_source.get(vid) or ""
            text = meta.get("text") or ""

            # law map lookup
            law_info = law_map.get(source) or {}
            law_title = law_info.get("law_title") or source
            law_short = law_info.get("law_short") or law_title

            refs = parse_law_refs(text)
            citation = build_citation(law_short, refs)

            # metadata enrich
            new_meta = meta.copy()
            new_meta.update({
                "law_title": law_title,
                "law_short": law_short,
                "citation": citation,
                "article_no": refs.get("article_no"),
                "article_title": refs.get("article_title"),
                "clause_no": refs.get("clause_no"),
                "item_no": refs.get("item_no"),
                "span_policy": refs.get("span_policy"),
                "pipeline_version": meta.get("pipeline_version") or "indexing-v1",
            })

            # ✅ Pinecone에 보내기 전 null 제거/타입 정제 (필수)
            new_meta = sanitize_pinecone_metadata(new_meta)

            if s.dry_run:
                updated += 1
                continue

            # 1) metadata-only update 시도
            ok = try_update_metadata(index, s.pinecone_namespace, vid, new_meta)

            # 2) 실패하면 fetch 값 기반 upsert fallback
            if not ok:
                values = v.get("values")
                if values is None:
                    # include_values가 없거나 fetch 결과에 없을 수 있음
                    # 이 경우 업데이트가 어려움 (다시 fetch include_values 옵션이 필요할 수 있음)
                    raise RuntimeError(
                        f"[backfill] update not supported and values missing for id={vid}. "
                        "Try upgrading pinecone client or adjust fetch to include values."
                    )

                index.upsert(
                    vectors=[{"id": vid, "values": values, "metadata": new_meta}],
                    namespace=s.pinecone_namespace,
                )

            updated += 1

    print(f"[backfill] done. updated={updated}, missing={missing}")


if __name__ == "__main__":
    main()
