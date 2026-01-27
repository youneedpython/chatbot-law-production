/***************************************************************
 * App.jsx
 * - Chatbot Law Production Frontend Entry
 * - session_id 기반 채팅 상태 관리
 * - Backend history API 연동
 ***************************************************************/

import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import ChatInput from "./components/ChatInput";
import ChatList from "./components/ChatList";
import { apiFetch } from "./api/client";

import "./App.css";

function ensureSessionId(current) {
  if (current) return current;
  return crypto?.randomUUID?.() ?? String(Date.now());
}

export default function App() {
  const navigate = useNavigate();
  const { session_id: routeSessionId } = useParams();

  const [sessionId, setSessionId] = useState("");
  const [input, setInput] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);

  const storageKey = useMemo(
    () => (sessionId ? `chat_history_${sessionId}` : ""),
    [sessionId]
  );

  useEffect(() => {
    const sid = ensureSessionId(routeSessionId);
    setSessionId(sid);
    if (routeSessionId !== sid) {
      navigate(`/chat/${sid}`, { replace: true });
    }
  }, [routeSessionId, navigate]);

  /**
   * 서버에서 히스토리 로드
   */
  useEffect(() => {
    if (!sessionId) return;

    const controller = new AbortController();

    (async () => {
      try {
        const res = await apiFetch(
          `/conversations/${sessionId}/messages?limit=100`,
          { signal: controller.signal }
        );

        if (!res.ok) {
          if (res.status === 404) {
            setHistory([]);
            return;
          }
          throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();
        const msgs = Array.isArray(data?.messages) ? data.messages : [];
        setHistory(
          msgs.map((m) => ({
            role: m.role,
            content: m.content,
            sources: m.sources || [],
          }))
        );
      } catch (e) {
        if (e.name === "AbortError") return;
        console.error(e);
        setHistory([]);
      }
    })();

    return () => controller.abort();
  }, [sessionId]);

  async function send() {
    const message = input.trim();
    if (!message || loading) return;

    setHistory((p) => [...p, { role: "user", content: message, sources: [] }]);
    setInput("");
    setLoading(true);

    try {
      const res = await apiFetch(`/chat/${sessionId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      setHistory((p) => [
        ...p,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources || [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      {/* ✅ container를 "채팅 앱 레이아웃"으로 사용 */}
      <div className="container chatLayout">
        {/* (선택) 상단 제목: ChatGPT처럼 심플하게 */}
        <div className="header">
          <h1 className="title">챗봇</h1>
          <p className="subtitle">전세사기 피해자 법률 상담</p>
        </div>

        {/* ✅ 메시지 영역: 여기만 스크롤 */}
          <ChatList
            history={history}
            loading={loading}
            copiedIndex={copiedIndex}
            onCopy={async (text, idx) => {
              await navigator.clipboard.writeText(text);
              setCopiedIndex(idx);
              setTimeout(() => setCopiedIndex(null), 1200);
            }}
          />

        {/* ✅ 입력창: 하단 고정(sticky) */}
        <div className="chatInputDock">
          <div className="chatInputInner">
          <ChatInput
            value={input}
            onChange={setInput}
            onSend={send}
            onKeyDown={(e) => e.key === "Enter" && send()}
            disabled={loading}
          />
          </div>
        </div>
      </div>
    </div>
  );
}
