"""Index API endpoints for document uploading and status."""

import asyncio
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ModelProvider, settings
from app.database import async_session_maker, get_db_session
from app.schemas import (
    ActivateGraphResponseSchema,
    DeleteCurrentIndexResponseSchema,
    DocumentStatusSchema,
    IndexedGraphListResponseSchema,
    IndexedGraphSchema,
    IndexProgressSchema,
    IndexStatusResponseSchema,
    UploadResponseSchema,
)
from app.services.graphrag import (
    GeminiConfigurationError,
    GraphRAGError,
    GraphRAGService,
    IndexingError,
    OllamaConnectionError,
    OpenRouterConfigurationError,
    graphrag_service,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@dataclass
class IndexJob:
    """In-memory progress state for one indexing job."""

    document_id: UUID
    graph_id: UUID
    filename: str
    status: str
    progress: int
    message: str
    chunks_processed: int | None = None
    total_chunks: int | None = None
    current_chunk: int | None = None
    current_chunk_progress: int | None = None
    phase: str | None = None
    phase_processed: int | None = None
    phase_total: int | None = None
    phase_progress: int | None = None
    entity_count: int | None = None
    relationship_count: int | None = None
    error: str | None = None


index_jobs: dict[UUID, IndexJob] = {}
index_lock = asyncio.Lock()


def graph_row_to_schema(row: object) -> IndexedGraphSchema:
    """Convert a SQLAlchemy mapping/row into an indexed graph schema."""
    data = dict(row._mapping if hasattr(row, "_mapping") else row)  # type: ignore[arg-type]
    return IndexedGraphSchema(**data)


async def infer_migrated_graph_filename(db: AsyncSession) -> str:
    """Infer a user-facing filename for a migrated root GraphRAG workspace."""
    result = await db.execute(
        text("""
            SELECT filename
            FROM indexed_documents
            WHERE filename IS NOT NULL AND filename <> ''
            ORDER BY indexed_at DESC
            LIMIT 1
        """)
    )
    row = result.fetchone()
    if row and row.filename:
        return str(row.filename)

    input_dir = graphrag_service.base_graphrag_root / "input"
    input_files = sorted(
        input_dir.glob("*.txt"),
        key=lambda path: (-path.stat().st_mtime, path.name),
    )
    if input_files:
        return input_files[0].name

    return "Migrated index"


async def repair_legacy_graph_names(db: AsyncSession) -> None:
    """Replace old placeholder graph labels with the original indexed filename."""
    inferred_filename = await infer_migrated_graph_filename(db)
    await db.execute(
        text("""
            UPDATE indexed_graphs
            SET name = :filename,
                source_filename = :filename
            WHERE name = 'Legacy graph'
               OR source_filename = 'legacy-index'
        """),
        {"filename": inferred_filename},
    )


async def ensure_legacy_graph_catalog(db: AsyncSession) -> None:
    """Import a pre-multi-graph root output directory as one graph catalog row."""
    count_result = await db.execute(text("SELECT COUNT(*) FROM indexed_graphs"))
    if (count_result.scalar() or 0) > 0:
        await repair_legacy_graph_names(db)
        return

    root_output = graphrag_service.base_graphrag_root / "output"
    if not (root_output / "entities.parquet").exists() and not (
        root_output / "relationships.parquet"
    ).exists():
        return

    graph_id = uuid4()
    workspace_path = graphrag_service.graph_workspace_path(graph_id)
    graphrag_service.ensure_workspace_config(workspace_path)
    for directory in ("input", "output", "cache"):
        source = graphrag_service.base_graphrag_root / directory
        target = workspace_path / directory
        if source.exists():
            shutil.copytree(source, target, dirs_exist_ok=True)

    source_filename = await infer_migrated_graph_filename(db)
    stats = graphrag_service.get_stats()
    await db.execute(
        text("""
            INSERT INTO indexed_graphs (
                id, name, source_filename, status, entity_count, relationship_count,
                workspace_path, is_active, indexed_at, activated_at
            )
            VALUES (
                :id, :name, :source_filename, 'completed', :entity_count,
                :relationship_count, :workspace_path, TRUE, CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
        """),
        {
            "id": graph_id,
            "name": source_filename,
            "source_filename": source_filename,
            "entity_count": stats.get("entity_count", 0),
            "relationship_count": stats.get("relationship_count", 0),
            "workspace_path": str(workspace_path),
        },
    )
    await db.execute(
        text("""
            UPDATE indexed_documents
            SET graph_id = :graph_id
            WHERE graph_id IS NULL
        """),
        {"graph_id": graph_id},
    )
    await db.execute(
        text("""
            UPDATE conversations
            SET graph_id = :graph_id
            WHERE graph_id IS NULL
        """),
        {"graph_id": graph_id},
    )
    graphrag_service.activate_graph_workspace(graph_id, workspace_path)
    await repair_legacy_graph_names(db)


async def get_graph_row(db: AsyncSession, graph_id: UUID):
    """Fetch one indexed graph row."""
    result = await db.execute(
        text("""
            SELECT id, name, source_filename, status, entity_count, relationship_count,
                   index_chat_provider, index_embed_provider, index_chat_model,
                   index_embed_model, is_active, created_at, indexed_at, activated_at, error,
                   workspace_path
            FROM indexed_graphs
            WHERE id = :id
        """),
        {"id": graph_id},
    )
    return result.fetchone()


async def activate_graph(db: AsyncSession, graph_id: UUID) -> IndexedGraphSchema:
    """Activate a completed graph in the database and GraphRAG service."""
    row = await get_graph_row(db, graph_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Graph not found")
    if row.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only completed graphs can be activated",
        )

    graphrag_service.activate_graph_workspace(graph_id, Path(row.workspace_path))
    await db.execute(text("UPDATE indexed_graphs SET is_active = FALSE"))
    await db.execute(
        text("""
            UPDATE indexed_graphs
            SET is_active = TRUE, activated_at = CURRENT_TIMESTAMP
            WHERE id = :id
        """),
        {"id": graph_id},
    )
    await db.commit()

    refreshed = await get_graph_row(db, graph_id)
    if refreshed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Graph not found")
    return graph_row_to_schema(refreshed)


def update_index_job(
    document_id: UUID,
    *,
    status: str | None = None,
    progress: int | None = None,
    message: str | None = None,
    chunks_processed: int | None = None,
    total_chunks: int | None = None,
    current_chunk: int | None = None,
    current_chunk_progress: int | None = None,
    phase: str | None = None,
    phase_processed: int | None = None,
    phase_total: int | None = None,
    phase_progress: int | None = None,
    entity_count: int | None = None,
    relationship_count: int | None = None,
    error: str | None = None,
) -> None:
    """Update progress for a running indexing job and log it for console visibility."""
    job = index_jobs.get(document_id)
    if not job:
        return

    if status is not None:
        job.status = status
    if progress is not None:
        job.progress = max(0, min(progress, 100))
    if message is not None:
        job.message = message
    if chunks_processed is not None:
        job.chunks_processed = chunks_processed
    if total_chunks is not None:
        job.total_chunks = total_chunks
    if current_chunk is not None:
        job.current_chunk = current_chunk
    if current_chunk_progress is not None:
        job.current_chunk_progress = max(0, min(current_chunk_progress, 100))
    if phase is not None:
        job.phase = phase
    if phase_processed is not None:
        job.phase_processed = phase_processed
    if phase_total is not None:
        job.phase_total = phase_total
    if phase_progress is not None:
        job.phase_progress = max(0, min(phase_progress, 100))
    if entity_count is not None:
        job.entity_count = entity_count
    if relationship_count is not None:
        job.relationship_count = relationship_count
    if error is not None:
        job.error = error

    logger.info(
        "Indexing %s: %s%% - %s%s",
        job.filename,
        job.progress,
        job.message,
        (
            f" ({job.phase}: {job.phase_processed}/{job.phase_total}, "
            f"{job.phase_progress}%)"
            if job.phase is not None
            and job.phase_processed is not None
            and job.phase_total is not None
            and job.phase_progress is not None
            else ""
        ),
    )


async def update_document_row(
    document_id: UUID,
    *,
    status_value: str,
    entity_count: int | None = None,
    relationship_count: int | None = None,
) -> None:
    """Persist the final document indexing status."""
    async with async_session_maker() as session:
        await session.execute(
            text("""
                UPDATE indexed_documents
                SET status = :status,
                    entity_count = :entity_count,
                    relationship_count = :relationship_count
                WHERE id = :id
            """),
            {
                "id": document_id,
                "status": status_value,
                "entity_count": entity_count,
                "relationship_count": relationship_count,
            },
        )
        await session.commit()


async def update_graph_row(
    graph_id: UUID,
    *,
    status_value: str,
    entity_count: int | None = None,
    relationship_count: int | None = None,
    error: str | None = None,
) -> None:
    """Persist indexing status for a graph catalog row."""
    async with async_session_maker() as session:
        if status_value == "completed":
            query = text("""
                UPDATE indexed_graphs
                SET status = :status,
                    entity_count = :entity_count,
                    relationship_count = :relationship_count,
                    indexed_at = CURRENT_TIMESTAMP,
                    error = :error
                WHERE id = :id
            """)
        else:
            query = text("""
                UPDATE indexed_graphs
                SET status = :status,
                    entity_count = :entity_count,
                    relationship_count = :relationship_count,
                    error = :error
                WHERE id = :id
            """)

        await session.execute(
            query,
            {
                "id": graph_id,
                "status": status_value,
                "entity_count": entity_count,
                "relationship_count": relationship_count,
                "error": error,
            },
        )
        await session.commit()


async def run_indexing_job(
    document_id: UUID,
    graph_id: UUID,
    filename: str,
    content: bytes,
    index_chat_provider: ModelProvider,
    index_embed_provider: ModelProvider,
) -> None:
    """Run one GraphRAG indexing job in the background."""
    async with index_lock:
        try:
            def update_progress(
                progress: int,
                message: str,
                chunks_processed: int | None = None,
                total_chunks: int | None = None,
                current_chunk: int | None = None,
                current_chunk_progress: int | None = None,
                phase: str | None = None,
                phase_processed: int | None = None,
                phase_total: int | None = None,
                phase_progress: int | None = None,
            ) -> None:
                update_index_job(
                    document_id,
                    status="indexing",
                    progress=progress,
                    message=message,
                    chunks_processed=chunks_processed,
                    total_chunks=total_chunks,
                    current_chunk=current_chunk,
                    current_chunk_progress=current_chunk_progress,
                    phase=phase,
                    phase_processed=phase_processed,
                    phase_total=phase_total,
                    phase_progress=phase_progress,
                )

            update_index_job(
                document_id,
                status="indexing",
                progress=5,
                message=(
                    f"Checking {index_chat_provider} chat and "
                    f"{index_embed_provider} embedding availability"
                ),
            )
            await update_graph_row(graph_id, status_value="processing")
            workspace_path = graphrag_service.graph_workspace_path(graph_id)
            if not workspace_path.resolve().is_relative_to(
                graphrag_service.graphs_root.resolve()
            ):
                raise IndexingError("Refusing to index outside the managed graph workspace root")

            worker = GraphRAGService()
            worker.use_workspace(workspace_path, graph_id)

            await worker.check_provider_health(index_chat_provider, model_kind="chat")
            await worker.check_provider_health(
                index_embed_provider,
                model_kind="embedding",
            )

            stats = await worker.index_document(
                filename,
                content,
                progress_callback=update_progress,
                index_chat_provider=index_chat_provider,
                index_embed_provider=index_embed_provider,
            )

            await update_document_row(
                document_id,
                status_value="completed",
                entity_count=stats["entity_count"],
                relationship_count=stats["relationship_count"],
            )
            await update_graph_row(
                graph_id,
                status_value="completed",
                entity_count=stats["entity_count"],
                relationship_count=stats["relationship_count"],
            )
            update_index_job(
                document_id,
                status="completed",
                progress=100,
                message="Indexing completed",
                entity_count=stats["entity_count"],
                relationship_count=stats["relationship_count"],
            )
        except Exception as e:
            logger.exception("Indexing job failed for %s", filename)
            await update_document_row(document_id, status_value="failed")
            await update_graph_row(graph_id, status_value="failed", error=str(e))
            update_index_job(
                document_id,
                status="failed",
                progress=100,
                message="Indexing failed",
                error=str(e),
            )


@router.post(
    "/upload",
    response_model=UploadResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model_provider: ModelProvider | None = Form(None),
    index_chat_provider: ModelProvider | None = Form(None),
    index_embed_provider: ModelProvider | None = Form(None),
    db: AsyncSession = Depends(get_db_session),
) -> UploadResponseSchema:
    """
    Upload a document for indexing with GraphRAG.

    Args:
        file: Uploaded text file.
        db: Database session.

    Returns:
        UploadResponseSchema: Upload result with statistics.
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required")

    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .txt files are supported",
        )

    try:
        # Read file content
        content = await file.read()

        if len(content) == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")

        # Save graph and document rows before the background job starts
        document_id = uuid4()
        graph_id = uuid4()
        workspace_path = graphrag_service.graph_workspace_path(graph_id)
        graph_name = file.filename
        active_index_chat_provider = (
            index_chat_provider or model_provider or settings.get_index_chat_provider()
        )
        active_index_embed_provider = (
            index_embed_provider
            or (model_provider if index_chat_provider is None else None)
            or settings.get_index_embed_provider()
        )
        index_jobs[document_id] = IndexJob(
            document_id=document_id,
            graph_id=graph_id,
            filename=file.filename,
            status="queued",
            progress=0,
            message="Document queued for indexing",
        )

        await db.execute(
            text("""
                INSERT INTO indexed_graphs (
                    id, name, source_filename, status, entity_count, relationship_count,
                    index_chat_provider, index_embed_provider, index_chat_model,
                    index_embed_model, workspace_path, is_active
                )
                VALUES (
                    :id, :name, :source_filename, 'queued', NULL, NULL,
                    :index_chat_provider, :index_embed_provider, :index_chat_model,
                    :index_embed_model, :workspace_path, FALSE
                )
            """),
            {
                "id": graph_id,
                "name": graph_name,
                "source_filename": file.filename,
                "index_chat_provider": active_index_chat_provider,
                "index_embed_provider": active_index_embed_provider,
                "index_chat_model": settings.get_model_name(active_index_chat_provider, "chat"),
                "index_embed_model": settings.get_model_name(
                    active_index_embed_provider,
                    "embedding",
                ),
                "workspace_path": str(workspace_path),
            },
        )

        query = text("""
            INSERT INTO indexed_documents (
                id, graph_id, filename, status, entity_count, relationship_count
            )
            VALUES (
                :id, :graph_id, :filename, :status, :entity_count, :relationship_count
            )
        """)

        await db.execute(
            query,
            {
                "id": document_id,
                "graph_id": graph_id,
                "filename": file.filename,
                "status": "processing",
                "entity_count": None,
                "relationship_count": None,
            },
        )
        await db.commit()

        background_tasks.add_task(
            run_indexing_job,
            document_id,
            graph_id,
            file.filename,
            content,
            active_index_chat_provider,
            active_index_embed_provider,
        )
        logger.info(
            "Queued indexing job for %s with chat=%s, embedding=%s",
            file.filename,
            active_index_chat_provider,
            active_index_embed_provider,
        )

        return UploadResponseSchema(
            status="queued",
            document_id=document_id,
            graph_id=graph_id,
            filename=file.filename,
            progress=0,
            message="Document queued for indexing",
        )

    except OllamaConnectionError as e:
        logger.error(f"Ollama connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama service is unavailable. Please ensure Ollama is running.",
        ) from e
    except GeminiConfigurationError as e:
        logger.error(f"Gemini configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini API is not configured. Please set APP_GEMINI_API_KEY.",
        ) from e
    except OpenRouterConfigurationError as e:
        logger.error(f"OpenRouter configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OpenRouter API is not configured or selected model is unavailable: {e}",
        ) from e
    except IndexingError as e:
        logger.error(f"Indexing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index document: {str(e)}",
        ) from e
    except GraphRAGError as e:
        logger.error(f"GraphRAG error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GraphRAG error: {str(e)}",
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error during upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload and index document",
        ) from e


@router.get("/graphs", response_model=IndexedGraphListResponseSchema)
async def list_indexed_graphs(
    db: AsyncSession = Depends(get_db_session),
) -> IndexedGraphListResponseSchema:
    """List all graph catalog entries and the active graph id."""
    try:
        await ensure_legacy_graph_catalog(db)
        result = await db.execute(
            text("""
                SELECT id, name, source_filename, status, entity_count, relationship_count,
                       index_chat_provider, index_embed_provider, index_chat_model,
                       index_embed_model, is_active, created_at, indexed_at, activated_at, error
                FROM indexed_graphs
                ORDER BY created_at DESC
            """)
        )
        graphs = [graph_row_to_schema(row) for row in result.fetchall()]
        active_graph = next((graph for graph in graphs if graph.is_active), None)
        return IndexedGraphListResponseSchema(
            graphs=graphs,
            active_graph_id=active_graph.id if active_graph else None,
            total_graphs=len(graphs),
        )
    except Exception as e:
        logger.error(f"Failed to list indexed graphs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list indexed graphs",
        ) from e


@router.get("/graphs/active", response_model=IndexedGraphSchema | None)
async def get_active_graph(
    db: AsyncSession = Depends(get_db_session),
) -> IndexedGraphSchema | None:
    """Return the active graph catalog entry, if any."""
    try:
        await ensure_legacy_graph_catalog(db)
        result = await db.execute(
            text("""
                SELECT id, name, source_filename, status, entity_count, relationship_count,
                       index_chat_provider, index_embed_provider, index_chat_model,
                       index_embed_model, is_active, created_at, indexed_at, activated_at, error
                FROM indexed_graphs
                WHERE is_active = TRUE
                LIMIT 1
            """)
        )
        row = result.fetchone()
        return graph_row_to_schema(row) if row else None
    except Exception as e:
        logger.error(f"Failed to get active graph: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get active graph",
        ) from e


@router.post("/graphs/{graph_id}/activate", response_model=ActivateGraphResponseSchema)
async def activate_indexed_graph(
    graph_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> ActivateGraphResponseSchema:
    """Activate a completed indexed graph for graph view and chat queries."""
    try:
        await ensure_legacy_graph_catalog(db)
        graph = await activate_graph(db, graph_id)
        return ActivateGraphResponseSchema(graph=graph)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to activate graph {graph_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate indexed graph",
        ) from e


@router.delete("/current", response_model=DeleteCurrentIndexResponseSchema)
async def delete_current_index(
    db: AsyncSession = Depends(get_db_session),
) -> DeleteCurrentIndexResponseSchema:
    """Delete the active indexed graph and mark its documents as deleted."""
    async with index_lock:
        try:
            await ensure_legacy_graph_catalog(db)
            active_result = await db.execute(
                text("""
                    SELECT id, workspace_path
                    FROM indexed_graphs
                    WHERE is_active = TRUE
                    LIMIT 1
                """)
            )
            active_row = active_result.fetchone()
            if active_row is None:
                return DeleteCurrentIndexResponseSchema(
                    status="deleted",
                    message="No active indexed graph was loaded",
                )

            graph_id = active_row.id
            workspace_path = Path(active_row.workspace_path)
            if workspace_path.exists() and workspace_path.is_relative_to(
                graphrag_service.graphs_root
            ):
                shutil.rmtree(workspace_path)

            await db.execute(
                text("""
                    UPDATE indexed_documents
                    SET status = 'deleted',
                        entity_count = NULL,
                        relationship_count = NULL
                    WHERE graph_id = :graph_id
                """)
                ,
                {"graph_id": graph_id},
            )
            await db.execute(
                text("""
                    UPDATE indexed_graphs
                    SET status = 'deleted',
                        is_active = FALSE,
                        entity_count = NULL,
                        relationship_count = NULL
                    WHERE id = :graph_id
                """),
                {"graph_id": graph_id},
            )
            await db.commit()
            for document_id, job in list(index_jobs.items()):
                if job.graph_id == graph_id:
                    index_jobs.pop(document_id, None)
            graphrag_service.active_graph_id = None
            graphrag_service._invalidate_cached_index()

            return DeleteCurrentIndexResponseSchema(
                status="deleted",
                message="Current indexed graph was deleted",
            )
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete current index: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete current indexed graph",
            ) from e


@router.get("/progress/{document_id}", response_model=IndexProgressSchema)
async def get_index_progress(document_id: UUID) -> IndexProgressSchema:
    """
    Get percentage progress for a running or recently completed indexing job.

    Args:
        document_id: Document/job UUID returned by upload.

    Returns:
        IndexProgressSchema: Current indexing progress.
    """
    job = index_jobs.get(document_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Indexing progress is unavailable for this document",
        )

    return IndexProgressSchema(
        document_id=job.document_id,
        graph_id=job.graph_id,
        filename=job.filename,
        status=job.status,
        progress=job.progress,
        message=job.message,
        chunks_processed=job.chunks_processed,
        total_chunks=job.total_chunks,
        current_chunk=job.current_chunk,
        current_chunk_progress=job.current_chunk_progress,
        phase=job.phase,
        phase_processed=job.phase_processed,
        phase_total=job.phase_total,
        phase_progress=job.phase_progress,
        entity_count=job.entity_count,
        relationship_count=job.relationship_count,
        error=job.error,
    )


@router.get("/status", response_model=IndexStatusResponseSchema)
async def get_index_status(
    db: AsyncSession = Depends(get_db_session),
) -> IndexStatusResponseSchema:
    """
    Get status of all indexed documents.

    Args:
        db: Database session.

    Returns:
        IndexStatusResponseSchema: List of indexed documents with statistics.
    """
    try:
        query = text("""
            SELECT id, graph_id, filename, indexed_at, status, entity_count, relationship_count
            FROM indexed_documents
            ORDER BY indexed_at DESC
        """)

        result = await db.execute(query)
        rows = result.fetchall()

        documents = [
            DocumentStatusSchema(
                id=row[0],
                graph_id=row[1],
                filename=row[2],
                indexed_at=row[3],
                status=row[4],
                entity_count=row[5],
                relationship_count=row[6],
            )
            for row in rows
        ]

        return IndexStatusResponseSchema(documents=documents, total_documents=len(documents))

    except Exception as e:
        logger.error(f"Failed to get index status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve index status",
        ) from e
