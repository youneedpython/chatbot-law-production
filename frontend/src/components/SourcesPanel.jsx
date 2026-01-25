import { useMemo, useState } from "react";

function formatTitle(s) {
  // 우선순위: citation > (law_short + article) > source
  if (s?.citation) return s.citation;

  const law = s?.law_short || s?.law_title;
  const artNo = s?.article_no;
  const artTitle = s?.article_title;

  if (law && artNo) {
    const t = artTitle ? `(${artTitle})` : "";
    return `${law} 제${artNo}조${t}`;
  }

  return s?.source || "unknown";
}

function dedupeSources(sources) {
  if (!Array.isArray(sources)) return [];
  const seen = new Set();
  const out = [];

  for (const s of sources) {
    const key = s?.citation || s?.chunk_id || `${s?.source}:${s?.doc_sha}:${s?.chunk_index}`;
    if (!key || seen.has(key)) continue;
    seen.add(key);
    out.push(s);
  }

  // id 재정렬(보이는 번호를 안정적으로)
  return out.map((s, i) => ({ ...s, id: i + 1 }));
}

export default function SourcesPanel({ sources }) {
  const [open, setOpen] = useState(false);

  const normalized = useMemo(() => dedupeSources(sources), [sources]);

  if (!normalized.length) return null;

  return (
    <div style={{ marginTop: 10, borderTop: "1px dashed #e5e7eb", paddingTop: 8 }}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        style={{
          background: "transparent",
          border: "none",
          padding: 0,
          cursor: "pointer",
          fontSize: 12,
          color: "#6b7280",
        }}
      >
        출처 {normalized.length}개 {open ? "▲" : "▼"}
      </button>

      {open && (
        <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 8 }}>
          {normalized.map((s) => (
            <div
              key={s.id}
              style={{
                padding: "8px 10px",
                border: "1px solid #eef2f7",
                borderRadius: 10,
                background: "#fafafa",
              }}
            >
              <div style={{ fontSize: 12, fontWeight: 600, color: "#111827" }}>
                [{s.id}] {formatTitle(s)}
              </div>

              {/* snippet은 있으면 신뢰감이 확 올라갑니다 */}
              {s?.snippet ? (
                <div style={{ marginTop: 4, fontSize: 12, color: "#4b5563", lineHeight: 1.4 }}>
                  {s.snippet}
                </div>
              ) : null}

              <div style={{ marginTop: 6, fontSize: 11, color: "#9ca3af" }}>
                {s?.chunk_id ? `chunk: ${s.chunk_id}` : null}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
