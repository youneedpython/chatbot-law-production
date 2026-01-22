from typing import List, Dict, Any, Optional
from pinecone import Pinecone

class PineconeStore:
    def __init__(self, index_name: str, namespace: str = "default"):
        self.pc = Pinecone()
        self.index = self.pc.Index(index_name)
        self.namespace = namespace

    def delete_by_source(self, source: str) -> None:
        # metadata에 source가 있어야 filter delete 가능
        self.index.delete(
            namespace=self.namespace,
            filter={"source": source},
        )

    def upsert(self, vectors: List[Dict[str, Any]]) -> None:
        self.index.upsert(vectors=vectors, namespace=self.namespace)
