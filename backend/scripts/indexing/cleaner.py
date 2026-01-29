import re

def light_clean(text: str) -> str:
    """
    법률문서 안전 정제(의미/구조 훼손 금지):
    - 공백 과다 정리
    - 과도한 빈 줄만 축소
    """
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
