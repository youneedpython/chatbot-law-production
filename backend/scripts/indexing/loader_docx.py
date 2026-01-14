from docx import Document
from typing import List, Dict

def load_docx(path: str) -> List[Dict]:
    """
    Returns a list of blocks with minimal structure.
    Each block: { "text": str, "para_index": int }
    """
    doc = Document(path)
    blocks = []
    for i, p in enumerate(doc.paragraphs):
        text = (p.text or "").strip()
        if not text:
            continue
        blocks.append({"text": text, "para_index": i})
    return blocks

def blocks_to_text(blocks: List[Dict]) -> str:
    return "\n".join(b["text"] for b in blocks)
