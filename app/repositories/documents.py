"""Document + chunk + embedding data access."""
import json

from sqlalchemy.orm import Session

from app.models.entities import Chunk, Document, Embedding
from app.services.embeddings import embedding_service


def create_document(
    db: Session,
    owner_id: int,
    title: str,
    content: str,
    source: str | None,
    chunks: list[str],
) -> Document:
    doc = Document(owner_id=owner_id, title=title, content=content, source=source)
    db.add(doc)
    db.flush()  # assign doc.id

    for idx, text in enumerate(chunks):
        chunk = Chunk(document_id=doc.id, index=idx, text=text)
        db.add(chunk)
        db.flush()
        vec = embedding_service.embed(text)
        db.add(
            Embedding(
                chunk_id=chunk.id,
                vector=embedding_service.encode_vector(vec),
                model="local-hash",
            )
        )

    db.commit()
    db.refresh(doc)
    return doc


def list_documents(db: Session, owner_id: int) -> list[Document]:
    return (
        db.query(Document)
        .filter(Document.owner_id == owner_id)
        .order_by(Document.created_at.desc())
        .all()
    )


def get_document(db: Session, doc_id: int, owner_id: int) -> Document | None:
    return (
        db.query(Document)
        .filter(Document.id == doc_id, Document.owner_id == owner_id)
        .first()
    )


def delete_document(db: Session, doc: Document) -> None:
    db.delete(doc)
    db.commit()


def search_chunks(
    db: Session,
    owner_id: int,
    query_embedding: list[float],
    top_k: int = 5,
) -> list[tuple[Chunk, float]]:
    """Hybrid-ish retrieval: vector similarity over the owner's chunks.

    Returns (chunk, score) sorted by descending similarity.
    """
    rows = (
        db.query(Chunk, Embedding)
        .join(Embedding, Embedding.chunk_id == Chunk.id)
        .join(Document, Document.id == Chunk.document_id)
        .filter(Document.owner_id == owner_id)
        .all()
    )

    scored: list[tuple[Chunk, float]] = []
    for chunk, emb in rows:
        vec = embedding_service.decode_vector(emb.vector)
        score = embedding_service.cosine_similarity(query_embedding, vec)
        scored.append((chunk, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]