/***************************************************************
 * ChatInput.jsx
 * - ChatGPT 스타일 하단 입력창
 * - textarea auto-resize (자동 줄바꿈 + 자동 높이)
 ***************************************************************/

import { useEffect, useRef } from "react";

export default function ChatInput({
  value,
  onChange,
  onSend,
  onKeyDown,
  disabled,
}) {
  const taRef = useRef(null);

  // value가 외부에서 바뀌어도(칩 클릭 즉시 전송/초기화 등) 높이 재계산
  useEffect(() => {
    const el = taRef.current;
    if (!el) return;

    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  }, [value]);

  const handleChange = (e) => {
    const next = e.target.value;
    onChange(next);

    const el = taRef.current;
    if (!el) return;

    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;

    const maxH = 160;
    el.style.overflowY = el.scrollHeight > maxH ? "auto" : "hidden";
  };

  const handleKeyDown = (e) => {
    // ✅ Shift+Enter: 줄바꿈 (그냥 통과)
    if (e.key === "Enter" && e.shiftKey) {
      // 상위 핸들러가 Enter로 전송하지 못하게 방지
      // (줄바꿈은 기본 동작으로 진행)
      return;
    }

    // ✅ Enter(단독): 전송
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!disabled && value.trim()) onSend();
      return;
    }

    // 그 외 키만 상위 핸들러로 전달 (선택)
    if (onKeyDown) onKeyDown(e);
  };

  return (
    <div className="chatInputDock">
      <div className="chatInputInner">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (!disabled && value.trim()) onSend();
          }}
        >
          <textarea
            ref={taRef}
            value={value}
            placeholder="질문을 입력하세요"
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            rows={1}
            aria-label="질문 입력"
          />
          <button type="submit" disabled={disabled || !value.trim()}>
            전송
          </button>
        </form>
      </div>
    </div>
  );
}
