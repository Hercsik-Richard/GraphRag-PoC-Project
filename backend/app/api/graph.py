"""Graph API endpoints for visualization and statistics."""

import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas import GraphDataSchema, GraphDiagnosticsSchema, GraphStatsSchema
from app.services.graphrag import graphrag_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/full", response_model=GraphDataSchema)
async def get_full_graph() -> GraphDataSchema:
    """
    Get the full knowledge graph in React Flow format.

    Returns:
        GraphDataSchema: Complete graph with nodes and edges.
    """
    try:
        graph_data = graphrag_service.get_full_graph()
        return GraphDataSchema(**graph_data)
    except Exception as e:
        logger.error(f"Failed to get full graph: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve graph data",
        ) from e


@router.get("/stats", response_model=GraphStatsSchema)
async def get_graph_stats() -> GraphStatsSchema:
    """
    Get graph statistics.

    Returns:
        GraphStatsSchema: Entity and relationship counts, indexing status.
    """
    try:
        stats = graphrag_service.get_stats()
        return GraphStatsSchema(**stats)
    except Exception as e:
        logger.error(f"Failed to get graph stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve graph statistics",
        ) from e


@router.get("/diagnostics", response_model=GraphDiagnosticsSchema)
async def get_graph_diagnostics() -> GraphDiagnosticsSchema:
    """
    Get graph quality diagnostics and provider configuration summary.

    Returns:
        GraphDiagnosticsSchema: Counts, graph quality signals, providers, and warnings.
    """
    try:
        diagnostics = graphrag_service.get_diagnostics()
        return GraphDiagnosticsSchema(**diagnostics)
    except Exception as e:
        logger.error(f"Failed to get graph diagnostics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve graph diagnostics",
        ) from e
