/***************************************************************
 * ChatMessage.jsx
 * - 단일 채팅 메시지 UI 컴포넌트
 * - user / assistant 역할에 따른 아바타 및 말풍선 렌더링
 * - assistant 메시지 복사 버튼 및 마크다운 렌더링 담당
 * - ✅ 본문 내 인용 앵커(⟦n⟧ 또는 [n])를 sources의 citation 라벨로 치환하여 표시
 *   예) "... 처벌됩니다 ⟦1⟧." -> "... 처벌됩니다 [전세사기피해자법 제25조]."
 ***************************************************************/

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { royAvatar, userAvatar } from "../assets/avatars";

/**
 * sources로부터 "id -> 사람이 읽을 수 있는 출처 라벨" 맵을 만든다.
 * 우선순위:
 * 1) citation (가장 우선)
 * 2) law_short/law_title + article_no(+ clause_no, article_title)
 * 3) source fallback
 */
function buildCitationLabel(src) {
  if (!src) return "";

  const citation = (src.citation ?? "").toString().trim();
  if (citation) return citation;

  const law = (src.law_short || src.law_title || "").toString().trim();
  const articleNo =
    src.article_no === 0 || src.article_no ? String(src.article_no).trim() : "";
  const clauseNo =
    src.clause_no === 0 || src.clause_no ? String(src.clause_no).trim() : "";
  const articleTitle = (src.article_title ?? "").toString().trim();

  const parts = [];
  if (law) parts.push(law);
  if (articleNo) parts.push(`제${articleNo}조`);
  if (clauseNo) parts.push(`제${clauseNo}항`);

  // 제목이 있으면 괄호로 (목적) 형태
  const base = parts.join(" ");
  if (base && articleTitle) return `${base}(${articleTitle})`;
  if (base) return base;

  const fallback = (src.source ?? "").toString().trim();
  return fallback || "";
}

function buildCitationMap(sources = []) {
  const map = new Map();
  if (!Array.isArray(sources)) return map;

  for (const s of sources) {
    const id = s?.id;
    if (id === undefined || id === null) continue;

    const label = buildCitationLabel(s);
    if (!label) continue;

    map.set(String(id), label);
  }

  return map;
}

/**
 * 안전장치:
 * - 모델이 답변에 "chunk:" 같은 내부 정보 출력하면 제거
 * - (선택) 답변 마지막에 "출처" 섹션(프론트에서 따로 뿌리던 형태)이 붙어오면 제거
 */
function sanitizeAnswer(text) {
  if (!text || typeof text !== "string") return text;

  let out = text;

  // 1) chunk: 라인 제거
  out = out
    .split(/\r?\n/)
    .filter((line) => !line.trim().toLowerCase().startsWith("chunk:"))
    .join("\n");

  // 2) 답변 하단 "출처" 섹션 제거 (라인 시작이 '출처'인 경우부터 끝까지)
  //    - 예: "\n출처\n1. ...\n2. ..."
  //    - '출처:' 형태도 대응
  out = out.replace(/\n(?:출처\s*:?\s*)\n[\s\S]*$/m, "");

  return out.trimEnd();
}

/**
 * 본문에서 인용 앵커를 찾아 sources의 citation 라벨로 치환한다.
 * - 지원 패턴:
 *   1) ⟦n⟧  (백엔드에서 권장)
 *   2) [n]   (모델이 직접 찍거나 기존 포맷)
 *
 * 결과:
 * - ⟦1⟧ -> [전세사기피해자법 제25조]
 * - [1]  -> [전세사기피해자법 제25조]
 */
function inlineCitations(text, sources) {
  if (!text || typeof text !== "string") return text;

  const citationMap = buildCitationMap(sources);

  const replaceByNum = (num, original) => {
    const label = citationMap.get(String(num));
    if (!label) return original; // 매칭 실패 시 원문 유지
    return `[${label}]`;
  };

  // ⟦n⟧ 우선 치환 후, 남아있는 [n]도 치환
  return text
    .replace(/⟦(\d+)⟧/g, (m, n) => replaceByNum(n, m))
    .replace(/\[(\d+)\]/g, (m, n) => replaceByNum(n, m));
}

export default function ChatMessage({
  role,
  content,
  sources,
  onCopy,
  showCopied,
}) {
  const isUser = role === "user";

  const finalContent = isUser
    ? content
    : inlineCitations(sanitizeAnswer(content), sources);

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        alignItems: "flex-start",
        gap: 10,
        marginBottom: 12,
      }}
    >
      {/* assistant avatar */}
      {!isUser && (
        <img
          src={royAvatar}
          alt="로이"
          width={32}
          height={32}
          decoding="async"
          style={{ borderRadius: "50%", flexShrink: 0 }}
        />
      )}

      {/* bubble */}
      <div
        style={{
          maxWidth: "75%",
          border: "1px solid #e5e7eb",
          borderRadius: 12,
          padding: "10px 12px",
          background: isUser ? "#f3f4f6" : "#ffffff",
          overflowWrap: "anywhere",
        }}
      >
        {!isUser && (
          <div
            style={{
              display: "flex",
              justifyContent: "flex-end",
              marginBottom: 8,
            }}
          >
            <button className="copy-btn" onClick={onCopy}>
              📋 복사
              {showCopied && <span className="copy-tooltip">복사했습니다.</span>}
            </button>
          </div>
        )}

        {isUser ? (
          <div style={{ whiteSpace: "pre-wrap" }}>{finalContent}</div>
        ) : (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {finalContent}
          </ReactMarkdown>
        )}
      </div>

      {/* user avatar */}
      {isUser && (
        <img
          src={userAvatar}
          alt="사용자"
          width={32}
          height={32}
          decoding="async"
          style={{ borderRadius: "50%", flexShrink: 0 }}
        />
      )}
    </div>
  );
}
