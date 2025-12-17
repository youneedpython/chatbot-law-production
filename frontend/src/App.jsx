/***************************************************************
** Frontend App Component
** 입력 -> 전송 -> 백엔드 호출 -> 답변 표시 
****************************************************************/
import { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";


function getSessionIdFrmPath() {
  const parts = window.location.pathname.split("/").filter(Boolean);

  // /chat/:session_id 형태인지 확인
  if (parts[0] === 'chat' && parts[1]) 
    return parts[1];
  return null;
}

export default function App() {
  const { session_id } = useParams();  
  const navigate = useNavigate();

  // [상태 변수] message (사용자 입력), answer (챗봇 답변)
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState([]); // 누적 대화
  const [loading, setLoading] = useState(false);

  const [sessionId, setSessionId] = useState(session_id ?? null);

  // 세션ID가 생기면 URL을 /chat/{sessionId}로 유지
  useEffect(() => {
    if (!sessionId) 
      return;

    const newPath = `/chat/${sessionId}`;
    if (window.location.pathname !== newPath){
      window.history.replaceState(null, '', newPath);
    }
  }, [sessionId]);

  // API URL: vite proxy 사용 중이면 /api로 호출
  const apiBase = useMemo(() => '/api', []);

  // [전송 버튼] 챗봇에 메시지를 보내고 답변을 받는 함수
  async function onSend(e){
    e.preventDefault();
    const userText = message.trim();
    
    if(!userText || loading) 
      return;

    setMessage('');
    setLoading(true);

    // 1) user 메시지 추가
    setHistory((prev) => [...prev, {role: 'user', content: userText}]);

    // 2) assistant placeholder 추가 (나중에 교체)
    const placeholderId = crypto.randomUUID();
    setHistory((prev) => [
      ...prev,
      {role: 'assistant', content: '답변 생성 중...', id: placeholderId},
    ]);

    try {
      // path param 방식: /chat/{session_id}
      const url = sessionId ? `${apiBase}/chat/${sessionId}` : `${apiBase}/chat`;

      const res = await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        // session_id는 body에서 받도록 해두면 더 안전 (Backend가 허용한다면)
        body: JSON.stringify({message: userText, session_id: sessionId}),
      });

      if (!res.ok) 
        throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      
      // sessionId가 없었으면 새로 설정
      if (data?.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      // 3) placeholder를 실제 답변으로 교체
      setHistory((prev) => 
        prev.map((m) =>
          m.id === placeholderId
            ? {...m, content: data.answer || '답변이 없습니다.'}
            : m
        )
      );
    } catch (error) {
      setHistory((prev) =>
        prev.map((m) =>
          m.id === placeholderId
            ? { ...m, content: "서버 요청에 실패했습니다. 잠시 후 다시 시도해주세요." }
            : m
        )
      );
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  // UI 렌더링
  return (
      <div style={{ maxWidth: 1000, margin: "40px auto", padding: 24 }}>
        <h1>전세사기피해 상담 챗봇 (Production MVP)</h1>

        <form onSubmit={onSend} style={{ display: "flex", gap: 8, marginTop: 16 }}>
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="질문을 입력하세요"
            style={{ flex: 1, padding: 10, border: "1px solid #aaa" }}
          />
          <button type="submit" disabled={loading} style={{ padding: "10px 18px" }}>
            전송
          </button>
        </form>

        <div style={{ marginTop: 24 }}>
          <h3>대화</h3>

          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {history.map((m, idx) => (
              <div
                key={m.id ?? idx}
                style={{
                  whiteSpace: "pre-wrap",
                  padding: 12,
                  borderRadius: 8,
                  border: "1px solid #eee",
                  background: m.role === "user" ? "#f7f7ff" : "#ffffff",
                }}
              >
                <b>{m.role === "user" ? "나" : "챗봇"}</b>
                <div style={{ marginTop: 6 }}>{m.content}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
}
