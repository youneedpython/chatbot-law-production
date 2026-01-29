import React from "react";

export default function SuggestionChips({
  suggestions = [],
  onSelect,
}) {
  return (
    <section className="blank">
      <div className="blankCard">
        <div className="blankHeader">
          <h2 className="blankTitle">안녕하세요.</h2>
          <p className="blankDesc">
            전세사기 피해와 관련된 법률 정보를 도와드리는 상담 챗봇입니다.
            <br />
            아래 예시 질문을 클릭하면 바로 전송됩니다.
          </p>
        </div>

        <div className="blankLabel">질문 예시</div>

        <div className="chips" role="list">
          {suggestions.map((text, idx) => (
            <button
              key={`${idx}-${text}`}
              type="button"
              className="chip"
              onClick={() => onSelect?.(text)}
              role="listitem"
            >
              {text}
            </button>
          ))}
        </div>

        <p className="blankNote">
          ※ 안내: 본 답변은 참고용 정보이며, 구체적 사건은 전문가 상담이 필요할 수 있습니다.
        </p>
      </div>
    </section>
  );
}
