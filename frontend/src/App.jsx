/***************************************************************
 * App.jsx
 * - React(Chat UI) + FastAPI(/chat, /chat/{session_id}) MVP
 * - session_id는 URL path(/chat/:session_id)에 노출
 * - 대화 내역은 localStorage(chat_history_{sessionId})에 저장/복구
 * - 말풍선 UI, 자동 스크롤, 로딩/에러 UX 포함
 ***************************************************************/
import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import "./App.css";


// role별 표시(이모지)
const AVATAR = {
  user: "🙋‍♀️",       // 나
  assistant: "🤖",   // 챗봇
};


// 복사 함수
async function copyToClipboard(text) {  
  await navigator.clipboard.writeText(text);
}

function ChatMessage({ role, content }) {
  const isBot = role === "assistant";

  return (
    <div style={{ display: "flex", gap: 10, marginBottom: 12 }}>
      <div style={{ width: 28, textAlign: "center", fontSize: 20 }}>
        {AVATAR[role] ?? "💬"}
      </div>

      <div style={{
        flex: 1,
        border: "1px solid #e5e7eb",
        borderRadius: 10,
        padding: 12,
        background: isBot ? "#fff" : "#f7f7fb",
        position: "relative",
      }}>
        {/* 복사 버튼: 챗봇 답변에만 */}
        {isBot && (
          <button
            onClick={() => copyToClipboard(content)}
            style={{
              position: "absolute",
              top: 8,
              right: 8,
              fontSize: 12,
              padding: "6px 10px",
              borderRadius: 8,
              border: "1px solid #ddd",
              background: "white",
              cursor: "pointer",
            }}
            title="답변 복사"
          >
            📋 복사
          </button>
        )}

        {/* 마크다운 렌더: 챗봇만 / 유저는 일반 텍스트 */}
        {isBot ? (
          <div style={{ paddingRight: 70 }}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {content}
            </ReactMarkdown>
          </div>
        ) : (
          <div style={{ whiteSpace: "pre-wrap" }}>{content}</div>
        )}
      </div>
    </div>
  );
}


function safeJsonParse(value, fallback) {
  try {
    if (!value) return fallback;
    return JSON.parse(value);
  } catch {
    return fallback;
  }
}

function ensureSessionId(current) {
  if (current) return current;
  // 브라우저 지원 시 UUID 생성
  if (crypto?.randomUUID) return crypto.randomUUID();
  // fallback
  return String(Date.now());
}



export default function App() {
  const navigate = useNavigate();
  const { session_id: routeSessionId } = useParams();

  const [sessionId, setSessionId] = useState("");
  const [input, setInput] = useState("");
  const [history, setHistory] = useState([]); // [{role:'user'|'assistant', content:'...'}]
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [copiedIndex, setCopiedIndex] = useState(null);


  const bottomRef = useRef(null);

  const storageKey = useMemo(() => {
    if (!sessionId) return "";
    return `chat_history_${sessionId}`;
  }, [sessionId]);

  // 1) 최초 진입: URL의 session_id가 있으면 그걸 사용, 없으면 새로 생성해서 URL에 반영
  useEffect(() => {
    const sid = ensureSessionId(routeSessionId);
    setSessionId(sid);

    // URL이 /chat/:sid 형태가 아니면 교정 (replace)
    if (routeSessionId !== sid) {
      navigate(`/chat/${sid}`, { replace: true });
    }
  }, [routeSessionId, navigate]);

  // 2) sessionId 확정되면: localStorage에서 히스토리 복구
  useEffect(() => {
    if (!storageKey) return;
    const saved = safeJsonParse(localStorage.getItem(storageKey), []);
    setHistory(Array.isArray(saved) ? saved : []);
  }, [storageKey]);

  // 3) history 변경 시: localStorage에 저장 + 자동 스크롤
  useEffect(() => {
    if (!storageKey) return;
    localStorage.setItem(storageKey, JSON.stringify(history));

    // 새 메시지 추가될 때 아래로 이동
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, storageKey]);

  async function send() {
    const message = input.trim();
    if (!message || !sessionId || loading) return;

    setErrorMsg("");
    setLoading(true);

    // UI에 먼저 user 메시지 반영
    setHistory((prev) => [...prev, { role: "user", content: message }]);
    setInput("");

    try {
      // ✅ 백엔드가 /chat/{session_id}를 받도록 맞춘 형태
      // (vite proxy 기준: /api -> http://localhost:8000 로 proxy)
      const res = await fetch(`/api/chat/${sessionId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, session_id: sessionId }),
      });

      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(`HTTP ${res.status} ${res.statusText} ${text}`);
      }

      const data = await res.json();
      const answer = data?.answer ?? "";
      const returnedSessionId = data?.session_id ?? sessionId;

      // session_id가 바뀌는 설계라면 URL도 교정 가능 (현재는 고정이라 보통 동일)
      if (returnedSessionId && returnedSessionId !== sessionId) {
        setSessionId(returnedSessionId);
        navigate(`/chat/${returnedSessionId}`, { replace: true });
      }

      setHistory((prev) => [...prev, { role: "assistant", content: answer }]);
    } catch (e) {
      setErrorMsg(
        "답변 생성에 실패했어요. 잠시 후 다시 시도해 주세요. (백엔드 실행/키 설정 확인)"
      );
      // 실패해도 UX상 “assistant 실패 메시지”를 대화로 남기고 싶으면 아래 주석 해제
      // setHistory((prev) => [...prev, { role: "assistant", content: "⚠️ 답변 생성 실패" }]);
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  function onKeyDown(e) {
    // Enter로 전송, Shift+Enter는 줄바꿈(원하면 textarea로 바꿀 수 있음)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  function clearChat() {
    if (!storageKey) return;
    localStorage.removeItem(storageKey);
    setHistory([]);
    setErrorMsg("");
  }

  return (
    <div className="page">
      <div className="container">
        <div className="header">
          <h1 className="title">전세사기피해 상담 챗봇 (Production MVP)</h1>
          <p className="subtitle">
            session_id 기반 대화 + localStorage 히스토리 저장 (새로고침 유지)
          </p>
        </div>

        <div className="chatWrap">
          <div className="chatTop">
            <input
              className="input"
              value={input}
              placeholder="질문을 입력하세요"
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              disabled={loading}
            />
            <button className="sendBtn" onClick={send} disabled={loading || !input.trim()}>
              전송
            </button>
          </div>

          <div className="metaRow">
            <div className="sessionChip">session_id: {sessionId || "-"}</div>
            <button className="clearBtn" onClick={clearChat}>
              대화 지우기
            </button>
          </div>

          {errorMsg && <div className="errorBar">{errorMsg}</div>}

          <div className="chatBody">
            <div className="sectionLabel">대화</div>

            {history.map((m, idx) => {
  const isUser = m.role === "user";

  return (
    <div
      key={idx}
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        alignItems: "flex-start",
        gap: 10,
        marginBottom: 12,
      }}
    >
      {/* assistant avatar (왼쪽) */}
      {!isUser && (
        <div style={{ width: 32, textAlign: "center", fontSize: 20 }}>
          🤖
        </div>
      )}

      {/* bubble */}
      <div
        style={{
          maxWidth: "75%",
          border: "1px solid #e5e7eb",
          borderRadius: 12,
          padding: "10px 12px",
          background: isUser ? "#f3f4f6" : "#ffffff",
          whiteSpace: "pre-wrap",
          overflowWrap: "anywhere",
        }}
      >
        {/* (assistant만) 복사 버튼 */}
        {!isUser && (
          <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 8 }}>
            <button
              className="copy-btn"
              onClick={async () => {
                await navigator.clipboard.writeText(m.content ?? "");
                setCopiedIndex(idx);
                setTimeout(() => setCopiedIndex(null), 1200);
              }}
              aria-label="답변 복사"
            >
              📋 복사
              {copiedIndex === idx && <span className="copy-tooltip">복사했습니다.</span>}
            </button>
          </div>
        )}

        {/* markdown 렌더링 쓰는 경우 여기에서 렌더 */}
        {/* 예: <ReactMarkdown>{m.content}</ReactMarkdown> */}
        <div>{m.content}</div>
      </div>

      {/* user avatar (오른쪽) */}
      {isUser && (
        <div style={{ width: 32, textAlign: "center", fontSize: 20 }}>
          🙋‍♀️
        </div>
      )}
    </div>
  );
})}

            {loading && (
              <div className="msgRow assistant">
                <div className="bubble assistant">
                  <div className="bubbleHeader">챗봇</div>
                  <span className="typingDots" aria-label="typing">
                    <span />
                    <span />
                    <span />
                  </span>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        </div>
      </div>
    </div>
  );
}
