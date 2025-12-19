/***************************************************************
 * App.jsx
 * - Chatbot Law Production Frontend Entry
 * - session_id 기반 채팅 상태 관리
 * - localStorage 히스토리 로드/저장
 * - ChatInput / ChatList 조합 및 API 호출 제어
 *
 * v0.4.0 준비 상태:
 * - 컴포넌트 분리 완료
 * - Backend history API 연동 예정
 ***************************************************************/


import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import ChatInput from "./components/ChatInput";
import ChatList from "./components/ChatList";

import "./App.css";

function ensureSessionId(current) {
  if (current) return current;
  return crypto?.randomUUID?.() ?? String(Date.now());
}

function safeJsonParse(v, f) {
  try {
    return JSON.parse(v) ?? f;
  } catch {
    return f;
  }
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
  * 로컬스토리지 로드
  */
  // useEffect(() => {
  //   if (!storageKey) 
  //     return;
  //   setHistory(safeJsonParse(localStorage.getItem(storageKey), []));
  // }, [storageKey]);

  /**
   * 로컬스토리지에 저장
   * SoT: Backend DB
   */
  // useEffect(() => {
  //   if (!storageKey) 
  //     return;
  //   localStorage.setItem(storageKey, JSON.stringify(history));
  // }, [history, storageKey]);

  /**
   * 서버에서 히스토리 로드
   * */
  useEffect(() => {
    if(!sessionId)
      return;

    const controller = new AbortController();

    (async () => {
      try {
        const res = await fetch(
          `/api/conversations/${sessionId}/messages?limit=100`,
          { signal: controller.signal}
        );

        if (!res.ok) {
          // 대화가 아직 없으면, 서버에서 빈 배열로 처리할 수도 있어서
          // 404면 빈 히스토리로 시작
          if (res.status === 404) {
            setHistory([]);
            return;
          }
          throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();
        const msgs = Array.isArray(data?.messages) ? data.messages : [];
        setHistory(msgs.map((m) => ({ role: m.role, content: m.content })));
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

    setHistory((p) => [...p, { role: "user", content: message }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`/api/chat/${sessionId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      if (!res.ok)
        throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      setHistory((p) => [...p, { role: "assistant", content: data.answer }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="container">
        <ChatInput
          value={input}
          onChange={setInput}
          onSend={send}
          onKeyDown={(e) => e.key === "Enter" && send()}
          disabled={loading}
        />

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
      </div>
    </div>
  );
}
