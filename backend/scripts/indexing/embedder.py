from typing import List
from langchain_openai import OpenAIEmbeddings

class Embedder:
    def __init__(self, model: str):
        self.emb = OpenAIEmbeddings(model=model)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Use embed_documents for batching.
        """
        return self.emb.embed_documents(texts)
