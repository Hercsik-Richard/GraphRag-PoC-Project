"""Chat API endpoints for conversations and messages."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.schemas import (
    ConversationCreateSchema,
    ConversationSchema,
    DeleteResponseSchema,
    MessageSchema,
    QueryRequestSchema,
    QueryResponseSchema,
)
from app.services import chat as chat_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/conversations", response_model=ConversationSchema, status_code=status.HTTP_201_CREATED
)
async def create_conversation(
    conversation: ConversationCreateSchema,
    db: AsyncSession = Depends(get_db_session),
) -> ConversationSchema:
    """
    Create a new conversation.

    Args:
        conversation: Conversation creation data.
        db: Database session.

    Returns:
        ConversationSchema: Created conversation.
    """
    try:
        result = await chat_service.create_conversation(db, conversation.title)
        return ConversationSchema(**result)
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation",
        ) from e


@router.get("/conversations", response_model=list[ConversationSchema])
async def list_conversations(
    db: AsyncSession = Depends(get_db_session),
) -> list[ConversationSchema]:
    """
    List all conversations ordered by updated_at desc.

    Args:
        db: Database session.

    Returns:
        list[ConversationSchema]: List of conversations.
    """
    try:
        result = await chat_service.list_conversations(db)
        return [ConversationSchema(**conv) for conv in result]
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list conversations",
        ) from e


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageSchema])
async def get_messages(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> list[MessageSchema]:
    """
    Get all messages for a conversation ordered by created_at asc.

    Args:
        conversation_id: Conversation ID.
        db: Database session.

    Returns:
        list[MessageSchema]: List of messages.
    """
    # Check if conversation exists
    conversation = await chat_service.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    try:
        result = await chat_service.get_messages_by_conversation(db, conversation_id)
        return [MessageSchema(**msg) for msg in result]
    except Exception as e:
        logger.error(f"Failed to get messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get messages"
        ) from e


@router.post("/conversations/{conversation_id}/query", response_model=QueryResponseSchema)
async def query_conversation(
    conversation_id: UUID,
    query: QueryRequestSchema,
    db: AsyncSession = Depends(get_db_session),
) -> QueryResponseSchema:
    """
    Send a query to a conversation and get a response.

    Args:
        conversation_id: Conversation ID.
        query: User query.
        db: Database session.

    Returns:
        QueryResponseSchema: Query response with message and graph context.

    Raises:
        HTTPException: If conversation not found or query processing fails.
    """
    # Check if conversation exists
    conversation = await chat_service.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    try:
        # Process query with GraphRAG
        result = await chat_service.process_query(db, conversation_id, query.question)

        # Convert to response schema
        message = MessageSchema(**result["message"])
        retrieved_graph = result["retrieved_graph"]

        return QueryResponseSchema(message=message, retrieved_graph=retrieved_graph)

    except chat_service.QueryProcessingError as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}",
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in query endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your query",
        ) from e


@router.delete("/conversations/{conversation_id}", response_model=DeleteResponseSchema)
async def delete_conversation_endpoint(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> DeleteResponseSchema:
    """
    Delete a conversation and all its messages.

    Args:
        conversation_id: Conversation ID.
        db: Database session.

    Returns:
        DeleteResponseSchema: Deletion confirmation.
    """
    try:
        deleted = await chat_service.delete_conversation(db, conversation_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )
        return DeleteResponseSchema(status="deleted", id=conversation_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation",
        ) from e
