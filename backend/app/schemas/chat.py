"""Pydantic schemas for chat endpoints."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


SearchMode = Literal["auto", "local", "global", "drift"]
ResolvedSearchMode = Literal["local", "global", "drift"]


class ConversationCreateSchema(BaseModel):
    """Schema for creating a new conversation."""

    title: str = Field(..., min_length=1, max_length=500, description="Conversation title")


class ConversationSchema(BaseModel):
    """Schema for conversation response."""

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class MessageSchema(BaseModel):
    """Schema for message response."""

    id: UUID
    conversation_id: UUID
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str
    created_at: datetime
    retrieved_entities: list[dict[str, Any]] | None = None
    retrieved_relationships: list[dict[str, Any]] | None = None
    search_mode_used: ResolvedSearchMode | None = None
    search_mode_reason: str | None = None


class QueryRequestSchema(BaseModel):
    """Schema for chat query request."""

    question: str = Field(..., min_length=1, max_length=2000, description="User question")
    search_mode: SearchMode = Field(
        "auto",
        description="GraphRAG query mode. Auto routes to local, global, or DRIFT.",
    )


class RetrievedGraphSchema(BaseModel):
    """Schema for retrieved graph context."""

    entities: list[dict[str, Any]] = Field(default_factory=list)
    relationships: list[dict[str, Any]] = Field(default_factory=list)


class QueryResponseSchema(BaseModel):
    """Schema for query response with message and graph context."""

    message: MessageSchema
    retrieved_graph: RetrievedGraphSchema
    search_mode_used: ResolvedSearchMode
    search_mode_reason: str


class DeleteResponseSchema(BaseModel):
    """Schema for delete operation response."""

    status: str = "deleted"
    id: UUID
