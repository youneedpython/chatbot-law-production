from typing import List

## langchain v0.1.11에서 langchain_text_splitters 패키지를 별도로 분리하여 적용
## 따라서, 다음과 같이 별도로 패키지를 설치
## pip install -qU langchain-text-splitters
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_text(text)
