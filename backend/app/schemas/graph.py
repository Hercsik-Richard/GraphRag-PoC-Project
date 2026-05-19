"""Pydantic schemas for graph endpoints."""

from typing import Any

from pydantic import BaseModel, Field


class NodePositionSchema(BaseModel):
    """Schema for node position in visualization."""

    x: float
    y: float


class NodeDataSchema(BaseModel):
    """Schema for node data."""

    label: str
    type: str = "entity"
    description: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)
    aliases: list[str] = Field(default_factory=list)
    degree: int = 0
    component_id: int | None = None
    is_isolated: bool = False
    is_in_largest_component: bool = False
    generated_from_relationship: bool = False


class GraphNodeSchema(BaseModel):
    """Schema for React Flow node."""

    id: str
    data: NodeDataSchema
    position: NodePositionSchema
    type: str = "custom"


class EdgeDataSchema(BaseModel):
    """Schema for edge data."""

    weight: float = 1.0
    properties: dict[str, Any] = Field(default_factory=dict)
    original_source: str | None = None
    original_target: str | None = None
    endpoint_resolved: bool = False


class GraphEdgeSchema(BaseModel):
    """Schema for React Flow edge."""

    id: str
    source: str
    target: str
    label: str | None = None
    data: EdgeDataSchema = Field(default_factory=EdgeDataSchema)


class GraphDataSchema(BaseModel):
    """Schema for full graph data in React Flow format."""

    nodes: list[GraphNodeSchema] = Field(default_factory=list)
    edges: list[GraphEdgeSchema] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphStatsSchema(BaseModel):
    """Schema for graph statistics."""

    entity_count: int
    relationship_count: int
    indexed: bool
    last_indexed_at: str | None = None
