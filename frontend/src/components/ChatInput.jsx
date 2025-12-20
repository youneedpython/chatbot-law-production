/***************************************************************
 * ChatInput.jsx
 * - 채팅 입력 영역 컴포넌트
 * - 사용자 질문 입력 및 전송(Enter / 버튼) 담당
 * - 비즈니스 로직 없이 UI 이벤트만 위임
 ***************************************************************/


export default function ChatInput({
    value,
    onChange,
    onSend,
    onKeyDown,
    disabled,
}) {
    return (
    <div className="chatTop">
      <input
        className="input"
        value={value}
        placeholder="질문을 입력하세요"
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={onKeyDown}
        disabled={disabled}
      />
      <button
        className="sendBtn"
        onClick={onSend}
        disabled={disabled || !value.trim()}
      >
        전송
      </button>
    </div>
  );
}