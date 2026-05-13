from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app_name: str
    app_version: str
    llm_provider: str
    embedding_provider: str
    vectorstore: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=8000)
    top_k: int | None = Field(default=None, ge=1, le=20)


class SourceItem(BaseModel):
    source_id: str
    filename: str
    filepath: str
    score: float | None = None
    page: int | None = None
    preview: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
    source_count: int


class IngestResponse(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    vector_ids: list[str]

