"""Pydantic schemas for indexing endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentStatsSchema(BaseModel):
    """Schema for document indexing statistics."""

    entity_count: int
    relationship_count: int


class UploadResponseSchema(BaseModel):
    """Schema for document upload response."""

    status: str = "queued"
    document_id: UUID
    graph_id: UUID
    filename: str
    progress: int = 0
    message: str = "Document queued for indexing"
    stats: DocumentStatsSchema | None = None


class IndexProgressSchema(BaseModel):
    """Schema for a running indexing job."""

    document_id: UUID
    graph_id: UUID
    filename: str
    status: str
    progress: int = Field(ge=0, le=100)
    message: str
    chunks_processed: int | None = None
    total_chunks: int | None = None
    current_chunk: int | None = None
    current_chunk_progress: int | None = Field(default=None, ge=0, le=100)
    phase: str | None = None
    phase_processed: int | None = None
    phase_total: int | None = None
    phase_progress: int | None = Field(default=None, ge=0, le=100)
    entity_count: int | None = None
    relationship_count: int | None = None
    error: str | None = None


class DocumentStatusSchema(BaseModel):
    """Schema for indexed document status."""

    id: UUID
    graph_id: UUID | None = None
    filename: str
    indexed_at: datetime
    status: str
    entity_count: int | None = None
    relationship_count: int | None = None


class IndexStatusResponseSchema(BaseModel):
    """Schema for index status list response."""

    documents: list[DocumentStatusSchema] = Field(default_factory=list)
    total_documents: int


class DeleteCurrentIndexResponseSchema(BaseModel):
    """Schema for deleting the currently loaded GraphRAG index."""

    status: str = "deleted"
    message: str


class IndexedGraphSchema(BaseModel):
    """Schema for one indexed graph catalog entry."""

    id: UUID
    name: str
    source_filename: str
    status: str
    entity_count: int | None = None
    relationship_count: int | None = None
    index_chat_provider: str | None = None
    index_embed_provider: str | None = None
    index_chat_model: str | None = None
    index_embed_model: str | None = None
    is_active: bool = False
    created_at: datetime
    indexed_at: datetime | None = None
    activated_at: datetime | None = None
    error: str | None = None


class IndexedGraphListResponseSchema(BaseModel):
    """Schema for listing indexed graphs."""

    graphs: list[IndexedGraphSchema] = Field(default_factory=list)
    active_graph_id: UUID | None = None
    total_graphs: int


class ActivateGraphResponseSchema(BaseModel):
    """Schema returned after activating an indexed graph."""

    graph: IndexedGraphSchema
