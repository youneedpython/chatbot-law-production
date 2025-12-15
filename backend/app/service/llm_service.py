from openai import OpenAI
from app.core.config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_answer(user_message: str) -> str:
    if not OPENAI_API_KEY:
        return 'OPENAI_API_KEY가 설정되지 않았습니다. backend/ .env에 API 키를 추가해주세요.'

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {'role': 'system', 'content': 'You are a helpful legal assistant for Korean jeonse fraud victims.'},
            {'role': 'user', 'content': user_message},
        ],
    )

    return response.choices[0].message.content or ''