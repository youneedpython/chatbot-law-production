/***************************************************************
 * ChatMessage.jsx
 * - 단일 채팅 메시지 UI 컴포넌트
 * - user / assistant 역할에 따른 아바타 및 말풍선 렌더링
 * - assistant 메시지 복사 버튼 및 마크다운 렌더링 담당
 * - ✅ 본문 내 인용번호([1])를 sources의 citation 텍스트로 치환하여 표시
 ***************************************************************/

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { royAvatar, userAvatar } from "../assets/avatars";

/**
 * sources로부터 "id -> 사람이 읽을 수 있는 출처 라벨" 맵을 만든다.
 * 우선순위:
 * 1) citation
 * 2) law_short/law_title + article_no(+ article_title)
 * 3) source fallback
 */
function buildCitationMap(sources = []) {
  const map = new Map();
  if (!Array.isArray(sources)) return map;

  for (const s of sources) {
    const id = s?.id;
    if (id === undefined || id === null) continue;

    let label = "";

    if (s?.citation) {
      label = s.citation;
    } else {
      const law = s?.law_short || s?.law_title;
      const artNo = s?.article_no;
      const artTitle = s?.article_title;

      if (law && artNo) {
        label = `${law} 제${artNo}조${artTitle ? `(${artTitle})` : ""}`;
      } else if (s?.source) {
        label = s.source;
      }
    }

    if (!label) continue;
    map.set(String(id), label);
  }

  return map;
}

/**
 * 본문에서 [숫자] 패턴을 찾아 sources의 citation 라벨로 치환한다.
 * 예) "... 처벌됩니다 [1]." -> "... 처벌됩니다 [전세사기피해자법 제25조]."
 */
function replaceCitationNumbers(text, sources) {
  if (!text || typeof text !== "string") return text;

  const citationMap = buildCitationMap(sources);

  // [1], [12] 등 모두 처리
  return text.replace(/\[(\d+)\]/g, (match, num) => {
    const label = citationMap.get(String(num));
    if (!label) return match; // sources에 없으면 원문 유지
    return `[${label}]`;
  });
}

/**
 * 안전장치: 혹시 모델이 답변에 "chunk:" 같은 내부 정보를 출력하면 제거
 * (현재 요구사항상 사용자에게 불필요)
 */
function stripInternalLines(text) {
  if (!text || typeof text !== "string") return text;

  return text
    .split(/\r?\n/)
    .filter((line) => !line.trim().toLowerCase().startsWith("chunk:"))
    .join("\n");
}

export default function ChatMessage({
  role,
  content,
  sources,
  onCopy,
  showCopied,
}) {
  const isUser = role === "user";

  // ✅ assistant 응답에만 적용: [n] → [출처 텍스트]
  const finalContent = isUser
    ? content
    : replaceCitationNumbers(stripInternalLines(content), sources);

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
          <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 8 }}>
            <button className="copy-btn" onClick={onCopy}>
              📋 복사
              {showCopied && <span className="copy-tooltip">복사했습니다.</span>}
            </button>
          </div>
        )}

        {isUser ? (
          <div style={{ whiteSpace: "pre-wrap" }}>{finalContent}</div>
        ) : (
          <>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {finalContent}
            </ReactMarkdown>
          </>
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
