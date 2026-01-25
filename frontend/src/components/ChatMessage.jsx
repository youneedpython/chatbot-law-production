/***************************************************************
 * ChatMessage.jsx
 * - 단일 채팅 메시지 UI 컴포넌트
 * - user / assistant 역할에 따른 아바타 및 말풍선 렌더링
 * - assistant 메시지 복사 버튼 및 마크다운 렌더링 담당
 ***************************************************************/


import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { royAvatar, userAvatar } from "../assets/avatars";
import SourcesPanel from "./SourcesPanel";


export default function ChatMessage({
    role,
    content,
    sources, 
    onCopy,
    showCopied,
}){
    const isUser = role === "user";

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
          <div style={{ whiteSpace: "pre-wrap" }}>{content}</div>
        ) : (
          <>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {content}
            </ReactMarkdown>

            {/* ✅ 출처 패널: assistant 메시지에만 노출 */}
            <SourcesPanel sources={sources} />
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