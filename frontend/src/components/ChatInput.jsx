/***************************************************************
 * ChatInput.jsx
 * - ChatGPT 스타일 하단 입력창
 ***************************************************************/

export default function ChatInput({
  value,
  onChange,
  onSend,
  onKeyDown,
  disabled,
}) {
  return (
    <div className="chatInputDock">
      <div className="chatInputInner">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (!disabled && value.trim()) onSend();
          }}
        >
          <input
            value={value}
            placeholder="질문을 입력하세요"
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={onKeyDown}
            disabled={disabled}
          />
          <button
            type="submit"
            disabled={disabled || !value.trim()}
          >
            전송
          </button>
        </form>
      </div>
    </div>
  );
}
