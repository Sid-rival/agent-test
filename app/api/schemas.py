"""Pydantic request/response schemas."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str | None = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    source: str | None = None


class DocumentOut(BaseModel):
    id: int
    title: str
    source: str | None
    created_at: datetime
    chunk_count: int = 0

    model_config = {"from_attributes": True}


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievedChunk(BaseModel):
    document_id: int
    document_title: str
    chunk_index: int
    text: str
    score: float


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[RetrievedChunk]