"""Graph API endpoints for visualization and statistics."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.schemas import GraphDataSchema, GraphDiagnosticsSchema, GraphStatsSchema
from app.services.graphrag import graphrag_service

logger = logging.getLogger(__name__)
router = APIRouter()


async def ensure_active_graph_loaded(db: AsyncSession) -> None:
    """Load the active graph workspace into the GraphRAG service if needed."""
    result = await db.execute(
        text("""
            SELECT id, workspace_path
            FROM indexed_graphs
            WHERE is_active = TRUE AND status = 'completed'
            LIMIT 1
        """)
    )
    row = result.fetchone()
    if row and graphrag_service.active_graph_id != row.id:
        from pathlib import Path

        graphrag_service.activate_graph_workspace(row.id, Path(row.workspace_path))


@router.get("/full", response_model=GraphDataSchema)
async def get_full_graph(
    db: AsyncSession = Depends(get_db_session),
) -> GraphDataSchema:
    """
    Get the full knowledge graph in React Flow format.

    Returns:
        GraphDataSchema: Complete graph with nodes and edges.
    """
    try:
        await ensure_active_graph_loaded(db)
        graph_data = graphrag_service.get_full_graph()
        return GraphDataSchema(**graph_data)
    except Exception as e:
        logger.error(f"Failed to get full graph: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve graph data",
        ) from e


@router.get("/stats", response_model=GraphStatsSchema)
async def get_graph_stats(
    db: AsyncSession = Depends(get_db_session),
) -> GraphStatsSchema:
    """
    Get graph statistics.

    Returns:
        GraphStatsSchema: Entity and relationship counts, indexing status.
    """
    try:
        await ensure_active_graph_loaded(db)
        stats = graphrag_service.get_stats()
        return GraphStatsSchema(**stats)
    except Exception as e:
        logger.error(f"Failed to get graph stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve graph statistics",
        ) from e


@router.get("/diagnostics", response_model=GraphDiagnosticsSchema)
async def get_graph_diagnostics(
    db: AsyncSession = Depends(get_db_session),
) -> GraphDiagnosticsSchema:
    """
    Get graph quality diagnostics and provider configuration summary.

    Returns:
        GraphDiagnosticsSchema: Counts, graph quality signals, providers, and warnings.
    """
    try:
        await ensure_active_graph_loaded(db)
        diagnostics = graphrag_service.get_diagnostics()
        return GraphDiagnosticsSchema(**diagnostics)
    except Exception as e:
        logger.error(f"Failed to get graph diagnostics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve graph diagnostics",
        ) from e
