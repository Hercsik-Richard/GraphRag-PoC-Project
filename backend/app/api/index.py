"""Index API endpoints for document uploading and status."""

import asyncio
import logging
from dataclasses import dataclass
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session_maker, get_db_session
from app.schemas import (
    DocumentStatusSchema,
    IndexProgressSchema,
    IndexStatusResponseSchema,
    UploadResponseSchema,
)
from app.services.graphrag import (
    GeminiConfigurationError,
    GraphRAGError,
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
    filename: str
    status: str
    progress: int
    message: str
    chunks_processed: int | None = None
    total_chunks: int | None = None
    current_chunk: int | None = None
    current_chunk_progress: int | None = None
    entity_count: int | None = None
    relationship_count: int | None = None
    error: str | None = None


index_jobs: dict[UUID, IndexJob] = {}
index_lock = asyncio.Lock()


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
            f" ({job.chunks_processed}/{job.total_chunks} chunks, "
            f"current {job.current_chunk}: {job.current_chunk_progress}%)"
            if job.chunks_processed is not None and job.total_chunks is not None
            and job.current_chunk is not None and job.current_chunk_progress is not None
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


async def run_indexing_job(document_id: UUID, filename: str, content: bytes) -> None:
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
                )

            index_provider = settings.get_index_chat_provider()
            index_embed_provider = settings.get_index_embed_provider()
            update_index_job(
                document_id,
                status="indexing",
                progress=5,
                message=f"Checking {index_provider} chat and {index_embed_provider} embedding availability",
            )
            await graphrag_service.check_provider_health(index_provider, model_kind="chat")
            await graphrag_service.check_provider_health(
                index_embed_provider,
                model_kind="embedding",
            )

            stats = await graphrag_service.index_document(
                filename,
                content,
                progress_callback=update_progress,
            )

            await update_document_row(
                document_id,
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

        # Save a document row before the background job starts
        document_id = uuid4()
        index_jobs[document_id] = IndexJob(
            document_id=document_id,
            filename=file.filename,
            status="queued",
            progress=0,
            message="Document queued for indexing",
        )

        if settings.graphrag_replace_corpus_on_upload:
            await db.execute(
                text("""
                    UPDATE indexed_documents
                    SET status = 'superseded'
                    WHERE status IN ('processing', 'completed')
                """)
            )

        query = text("""
            INSERT INTO indexed_documents (
                id, filename, status, entity_count, relationship_count
            )
            VALUES (:id, :filename, :status, :entity_count, :relationship_count)
        """)

        await db.execute(
            query,
            {
                "id": document_id,
                "filename": file.filename,
                "status": "processing",
                "entity_count": None,
                "relationship_count": None,
            },
        )
        await db.commit()

        background_tasks.add_task(run_indexing_job, document_id, file.filename, content)
        logger.info("Queued indexing job for %s", file.filename)

        return UploadResponseSchema(
            status="queued",
            document_id=document_id,
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
        filename=job.filename,
        status=job.status,
        progress=job.progress,
        message=job.message,
        chunks_processed=job.chunks_processed,
        total_chunks=job.total_chunks,
        current_chunk=job.current_chunk,
        current_chunk_progress=job.current_chunk_progress,
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
            SELECT id, filename, indexed_at, status, entity_count, relationship_count
            FROM indexed_documents
            ORDER BY indexed_at DESC
        """)

        result = await db.execute(query)
        rows = result.fetchall()

        documents = [
            DocumentStatusSchema(
                id=row[0],
                filename=row[1],
                indexed_at=row[2],
                status=row[3],
                entity_count=row[4],
                relationship_count=row[5],
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
