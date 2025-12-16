/***************************************************************
** Frontend App Component
** 입력 -> 전송 -> 백엔드 호출 -> 답변 표시 
****************************************************************/
import { use, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";


export default function App() {
  const { session_id } = useParams();  
  const navigate = useNavigate();

  // [상태 변수] message (사용자 입력), answer (챗봇 답변)
  const [message, setMessage] = useState("");
  const [answer, setAnswer] = useState("");
  const [sessionId, setSessionId] = useState(session_id ?? null);


  // [전송 버튼] 챗봇에 메시지를 보내고 답변을 받는 함수
  const send = async () => {
    if (!message.trim()) return;
    setAnswer("답변 생성 중...");

    // 백엔드 /api/chat 엔드포인트에 메시지 전송
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    });

    // JSON 파싱 에러 방지 코드
    // 404, 500 등 에러 응답 처리
    if (!res.ok) {
      const text = await res.text();
      setAnswer(`HTTP ${res.status}\n${text}`);
      return;   
    }

    // 응답 데이터 파싱
    const data = await res.json();
    console.log("챗봇 답변:", data);
    
    // 응답에서 답변 추출
    // 답변 상태 변수 업데이트
    setAnswer(data.answer ?? "(no answer)"); 

    // 최초 응답 시 session_id 저장 및 URL 업데이트
    const newSessionId = data.session_id;
    if(!sessionId && newSessionId){
      setSessionId(newSessionId);
      navigate(`/chat/${newSessionId}`, { replace: true });
    }

  };

  // UI 렌더링
  return (
    <div style={{ maxWidth: 720, margin: "40px auto", padding: 16 }}>
      <h2>전세사기피해 상담 챗봇 (Production MVP)</h2>

      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <input
          style={{ flex: 1, padding: 10 }}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="질문을 입력하세요"
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <button onClick={send} style={{ padding: "10px 14px" }}>
          전송
        </button>
      </div>

      <div style={{ marginTop: 20, whiteSpace: "pre-wrap" }}>
        <strong>답변</strong>
        <div style={{ marginTop: 8 }}>{answer}</div>
      </div>
    </div>
  );
}
