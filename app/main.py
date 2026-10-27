"""RAG QA API â FastAPI application entrypoint."""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, documents
from app.core.config import settings
from app.core.database import Base, engine

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger("rag_qa")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Production-grade RAG document Q&A service: FastAPI backend, JWT auth, "
        "document ingestion with chunking + embeddings, hybrid retrieval, and a "
        "pluggable LLM generation layer."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured.")


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")