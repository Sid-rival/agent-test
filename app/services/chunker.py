"""Document chunking service."""
from app.core.config import settings


def chunk_text(text: str, size: int | None = None, overlap: int | None = None) -> list[str]:
    """Split text into overlapping chunks on paragraph boundaries.

    Paragraphs longer than ``size`` are hard-split into character windows with
    ``overlap``. Paragraphs shorter than ``size`` are grouped until the window
    is full. Guarantees no chunk exceeds ``size`` characters.
    """
    size = size if size is not None else settings.chunk_size
    overlap = overlap if overlap is not None else settings.chunk_overlap

    text = "\n".join(line.strip() for line in text.splitlines())
    text = text.strip()
    if not text:
        return []

    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    def flush():
        nonlocal current
        if current:
            chunks.append(current)
            current = ""

    for para in paragraphs:
        if len(para) > size:
            flush()
            start = 0
            while start < len(para):
                chunks.append(para[start : start + size])
                start += size - overlap
            continue
        if current and len(current) + len(para) + 2 > size:
            flush()
        current = (current + "\n\n" + para) if current else para
    flush()

    return chunks