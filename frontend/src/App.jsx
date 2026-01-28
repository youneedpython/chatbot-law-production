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
import SuggestionChips from "./components/SuggestionChips";

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


  // ✅ (추가) Suggestion Chips 문구 세트
  const suggestions = useMemo(
    () => [
      "전세사기 피해자로 인정받으려면 어떤 요건이 필요한가요?",
      "보증금을 돌려받을 수 있는 방법이 있나요?",
      "전세사기 특별법에서 지원해주는 내용은 무엇인가요?",
      "지금 당장 해야 할 법적 조치는 무엇인가요?",
      "임대인이 연락이 안 될 때 어떻게 해야 하나요?",
    ],
    []
  );

/**
   * ✅ (추가) 실제 전송 로직을 "텍스트 인자 기반"으로 분리
   * - input 상태에 의존하지 않고도 전송 가능
   * - 칩 클릭 시 즉시 전송에 필수
   */
  async function sendMessage(messageText) {
    const message = String(messageText ?? "").trim();
    if (!message || loading) return;

    // 유저 메시지 즉시 반영
    setHistory((p) => [...p, { role: "user", content: message, sources: [] }]);

    // input은 UI 입력창만 비움 (칩 전송이어도 UX 상 비워두는 게 자연스러움)
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
    } catch (e) {
      console.error(e);
      // (선택) 에러 메시지를 assistant bubble로 보여주고 싶다면 여기에서 push 가능
      setHistory((p) => [
        ...p,
        {
          role: "assistant",
          content:
            "요청 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // ✅ 기존 send()는 input -> sendMessage(input)로만 위임
  async function send() {
    await sendMessage(input);
  }

  // ✅ 대화가 0개이고, 로딩이 아닐 때만 "첫 화면" 노출
  const isBlank = history.length === 0 && !loading;

  return (
    <div className="page">
      {/* ✅ container를 "채팅 앱 레이아웃"으로 사용 */}
      <div className="container chatLayout">
        {/* (선택) 상단 제목: ChatGPT처럼 심플하게 */}
        <div className="header">
          <h1 className="title">챗봇</h1>
          <p className="subtitle">전세사기 피해자 법률 상담</p>
        </div>

        {/* ✅ Blank State: 대화가 없을 때는 SuggestionChips 보여주기 */}
        {isBlank ? (
          <SuggestionChips
            suggestions={suggestions}
            onSelect={(text) => sendMessage(text)} // ✅ 칩 클릭 즉시 전송
          />
        ) : (
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
        )}

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