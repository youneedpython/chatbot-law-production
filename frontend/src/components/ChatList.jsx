/***************************************************************
 * ChatList.jsx
 * - 채팅 메시지 목록 렌더링 컴포넌트
 * - 대화 히스토리 순회 렌더링
 * - 새 메시지 추가 시 자동 스크롤 처리
 ***************************************************************/


import { useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage"


export default function ChatList({ 
    history,
    loading,
    copiedIndex,
    onCopy 
}) {
    const bottomRef = useRef(null);

    // 새 메시지 도착 시 스크롤 최하단 이동
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [history, loading]);

    return (
    <div className="chatBody">
      {/* <div className="sectionLabel">...</div> */}

      {history.map((m, idx) => (
        <ChatMessage
          key={idx}
          role={m.role}
          content={m.content}
          sources={m.sources || []}  // ✅ 추가: assistant 메시지에 출처 전달
          onCopy={() => onCopy(m.content, idx)}
          showCopied={copiedIndex === idx}
        />
      ))}

      {loading && (
        <div className="msgRow assistant">
          <div className="bubble assistant">
            <span className="typingDots">
              <span />
              <span />
              <span />
            </span>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );

}