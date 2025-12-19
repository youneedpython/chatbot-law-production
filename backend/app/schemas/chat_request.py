"""
schemas/chat_request.py

/chat 엔드포인트에서 사용하는 채팅 요청(Request) 스키마 정의 파일

역할
- 사용자가 입력한 메시지(message)를 검증하여 API 계층에서 전달

설계 의도
- 채팅 오케스트레이션 전용 스키마로,
  대화 히스토리(MessageCreate) 스키마와 분리하여 책임을 명확히 함
- 향후 옵션(prompt 설정, temperature 등)이 추가되더라도
  history API와 독립적으로 확장 가능
"""


from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


