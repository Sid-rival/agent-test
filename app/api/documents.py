"""Document ingestion + RAG query routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import schemas
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.entities import User
from app.repositories import documents as doc_repo
from app.services.chunker import chunk_text
from app.services.embeddings import embedding_service
from app.services.llm import llm_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=schemas.DocumentOut, status_code=201)
def ingest(
    payload: schemas.DocumentCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    chunks = chunk_text(payload.content)
    doc = doc_repo.create_document(
        db, current.id, payload.title, payload.content, payload.source, chunks
    )
    return schemas.DocumentOut(
        id=doc.id,
        title=doc.title,
        source=doc.source,
        created_at=doc.created_at,
        chunk_count=len(chunks),
    )


@router.get("", response_model=list[schemas.DocumentOut])
def list_docs(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    docs = doc_repo.list_documents(db, current.id)
    out = []
    for d in docs:
        out.append(
            schemas.DocumentOut(
                id=d.id,
                title=d.title,
                source=d.source,
                created_at=d.created_at,
                chunk_count=len(d.chunks),
            )
        )
    return out


@router.delete("/{doc_id}", status_code=204)
def delete_doc(
    doc_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    doc = doc_repo.get_document(db, doc_id, current.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc_repo.delete_document(db, doc)


@router.post("/query", response_model=schemas.QueryResponse)
def query(
    payload: schemas.QueryRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    q_vec = embedding_service.embed(payload.question)
    hits = doc_repo.search_chunks(db, current.id, q_vec, payload.top_k)
    if not hits:
        return schemas.QueryResponse(
            question=payload.question,
            answer=llm_service.generate(payload.question, []),
            sources=[],
        )
    contexts = [chunk.text for chunk, _ in hits]
    answer = llm_service.generate(payload.question, contexts)
    sources = [
        schemas.RetrievedChunk(
            document_id=chunk.document_id,
            document_title=chunk.document.title,
            chunk_index=chunk.index,
            text=chunk.text,
            score=round(score, 4),
        )
        for chunk, score in hits
    ]
    return schemas.QueryResponse(
        question=payload.question,
        answer=answer,
        sources=sources,
    )