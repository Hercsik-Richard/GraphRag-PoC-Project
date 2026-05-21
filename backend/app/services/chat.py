"""Chat service for conversation and message operations using SQLAlchemy Core."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from graphrag.query.context_builder.conversation_history import (
    ConversationHistory,
)
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ModelProvider
from app.services.graphrag import GraphRAGError, SearchMode, graphrag_service

logger = logging.getLogger(__name__)


class QueryProcessingError(Exception):
    """Exception raised when query processing fails."""

    pass


async def create_conversation(
    db: AsyncSession,
    title: str,
    graph_id: UUID | None = None,
) -> dict[str, Any]:
    """
    Create a new conversation.

    Args:
        db: Database session.
        title: Conversation title.

    Returns:
        dict: Created conversation data.
    """
    conversation_id = uuid4()
    now = datetime.utcnow()

    query = text("""
        INSERT INTO conversations (id, graph_id, title, created_at, updated_at)
        VALUES (:id, :graph_id, :title, :created_at, :updated_at)
        RETURNING id, graph_id, title, created_at, updated_at
    """)

    result = await db.execute(
        query,
        {
            "id": conversation_id,
            "graph_id": graph_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
        },
    )

    row = result.fetchone()
    if row is None:
        raise RuntimeError("Failed to create conversation")

    return {
        "id": row[0],
        "graph_id": row[1],
        "title": row[2],
        "created_at": row[3],
        "updated_at": row[4],
    }


async def list_conversations(
    db: AsyncSession,
    graph_id: UUID | None = None,
) -> list[dict[str, Any]]:
    """
    List all conversations ordered by updated_at desc.

    Args:
        db: Database session.

    Returns:
        list: List of conversations.
    """
    if graph_id is None:
        query = text("""
            SELECT id, graph_id, title, created_at, updated_at
            FROM conversations
            WHERE graph_id IS NULL
            ORDER BY updated_at DESC
        """)
        params: dict[str, Any] = {}
    else:
        query = text("""
            SELECT id, graph_id, title, created_at, updated_at
            FROM conversations
            WHERE graph_id = :graph_id
            ORDER BY updated_at DESC
        """)
        params = {"graph_id": graph_id}

    result = await db.execute(query, params)
    rows = result.fetchall()

    return [
        {
            "id": row[0],
            "graph_id": row[1],
            "title": row[2],
            "created_at": row[3],
            "updated_at": row[4],
        }
        for row in rows
    ]


async def get_conversation_by_id(db: AsyncSession, conversation_id: UUID) -> dict[str, Any] | None:
    """
    Get a conversation by ID.

    Args:
        db: Database session.
        conversation_id: Conversation UUID.

    Returns:
        dict | None: Conversation data or None if not found.
    """
    query = text("""
        SELECT id, graph_id, title, created_at, updated_at
        FROM conversations
        WHERE id = :id
    """)

    result = await db.execute(query, {"id": conversation_id})
    row = result.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "graph_id": row[1],
        "title": row[2],
        "created_at": row[3],
        "updated_at": row[4],
    }


async def update_conversation_timestamp(db: AsyncSession, conversation_id: UUID) -> None:
    """
    Update conversation's updated_at timestamp.

    Args:
        db: Database session.
        conversation_id: Conversation UUID.
    """
    query = text("""
        UPDATE conversations
        SET updated_at = :updated_at
        WHERE id = :id
    """)

    await db.execute(query, {"id": conversation_id, "updated_at": datetime.utcnow()})


async def delete_conversation(db: AsyncSession, conversation_id: UUID) -> bool:
    """
    Delete a conversation and all its messages (cascade).

    Args:
        db: Database session.
        conversation_id: Conversation UUID.

    Returns:
        bool: True if deleted, False if not found.
    """
    query = text("""
        DELETE FROM conversations
        WHERE id = :id
        RETURNING id
    """)

    result = await db.execute(query, {"id": conversation_id})
    row = result.fetchone()

    return row is not None


async def get_messages_by_conversation(
    db: AsyncSession, conversation_id: UUID
) -> list[dict[str, Any]]:
    """
    Get all messages for a conversation ordered by created_at asc.

    Args:
        db: Database session.
        conversation_id: Conversation UUID.

    Returns:
        list: List of messages.
    """
    query = text("""
        SELECT id, conversation_id, role, content, created_at,
               retrieved_entities, retrieved_relationships,
               retrieved_sources, search_mode_used, search_mode_reason
        FROM messages
        WHERE conversation_id = :conversation_id
        ORDER BY created_at ASC
    """)

    result = await db.execute(query, {"conversation_id": conversation_id})
    rows = result.fetchall()

    return [
        {
            "id": row[0],
            "conversation_id": row[1],
            "role": row[2],
            "content": row[3],
            "created_at": row[4],
            "retrieved_entities": row[5],
            "retrieved_relationships": row[6],
            "retrieved_sources": row[7],
            "search_mode_used": row[8],
            "search_mode_reason": row[9],
        }
        for row in rows
    ]


async def save_message(
    db: AsyncSession,
    conversation_id: UUID,
    role: str,
    content: str,
    retrieved_entities: list[dict[str, Any]] | None = None,
    retrieved_relationships: list[dict[str, Any]] | None = None,
    retrieved_sources: list[dict[str, Any]] | None = None,
    search_mode_used: str | None = None,
    search_mode_reason: str | None = None,
) -> dict[str, Any]:
    """
    Save a message to the database.

    Args:
        db: Database session.
        conversation_id: Conversation UUID.
        role: Message role ('user' or 'assistant').
        content: Message content.
        retrieved_entities: Retrieved entities (for assistant messages).
        retrieved_relationships: Retrieved relationships (for assistant messages).

    Returns:
        dict: Saved message data.
    """
    message_id = uuid4()
    now = datetime.utcnow()

    query = text("""
        INSERT INTO messages (
            id, conversation_id, role, content, created_at,
            retrieved_entities, retrieved_relationships, retrieved_sources,
            search_mode_used, search_mode_reason
        )
        VALUES (
            :id, :conversation_id, :role, :content, :created_at,
            CAST(:retrieved_entities AS json), CAST(:retrieved_relationships AS json),
            CAST(:retrieved_sources AS json),
            :search_mode_used, :search_mode_reason
        )
        RETURNING id, conversation_id, role, content, created_at,
                  retrieved_entities, retrieved_relationships, retrieved_sources,
                  search_mode_used, search_mode_reason
    """)

    # Convert lists to JSON strings for PostgreSQL
    import json

    entities_json = json.dumps(retrieved_entities) if retrieved_entities else None
    relationships_json = json.dumps(retrieved_relationships) if retrieved_relationships else None
    sources_json = json.dumps(retrieved_sources) if retrieved_sources else None

    result = await db.execute(
        query,
        {
            "id": message_id,
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "created_at": now,
            "retrieved_entities": entities_json,
            "retrieved_relationships": relationships_json,
            "retrieved_sources": sources_json,
            "search_mode_used": search_mode_used,
            "search_mode_reason": search_mode_reason,
        },
    )

    row = result.fetchone()
    if row is None:
        raise RuntimeError("Failed to save message")

    # Update conversation timestamp
    await update_conversation_timestamp(db, conversation_id)

    return {
        "id": row[0],
        "conversation_id": row[1],
        "role": row[2],
        "content": row[3],
        "created_at": row[4],
        "retrieved_entities": row[5],
        "retrieved_relationships": row[6],
        "retrieved_sources": row[7],
        "search_mode_used": row[8],
        "search_mode_reason": row[9],
    }


async def ensure_conversation_graph_loaded(
    db: AsyncSession,
    conversation_id: UUID,
) -> tuple[UUID | None, Path | None]:
    """Resolve the graph attached to a conversation before querying."""
    conversation = await get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise QueryProcessingError("Conversation not found")

    graph_id = conversation.get("graph_id")
    if graph_id is None:
        active_result = await db.execute(
            text("""
                SELECT id, workspace_path
                FROM indexed_graphs
                WHERE is_active = TRUE AND status = 'completed'
                LIMIT 1
            """)
        )
        active_row = active_result.fetchone()
        if active_row is None:
            raise QueryProcessingError("No completed graph is active for this conversation")
        graph_id = active_row.id
        workspace_path = active_row.workspace_path
    else:
        graph_result = await db.execute(
            text("""
                SELECT id, status, workspace_path
                FROM indexed_graphs
                WHERE id = :graph_id
            """),
            {"graph_id": graph_id},
        )
        graph_row = graph_result.fetchone()
        if graph_row is None:
            raise QueryProcessingError("Conversation graph not found")
        if graph_row.status != "completed":
            raise QueryProcessingError("Conversation graph is not ready for querying")
        workspace_path = graph_row.workspace_path

    return graph_id, Path(workspace_path)


async def process_query(
    db: AsyncSession,
    conversation_id: UUID,
    question: str,
    search_mode: SearchMode = "auto",
    query_chat_provider: ModelProvider | None = None,
    query_embed_provider: ModelProvider | None = None,
) -> dict[str, Any]:
    """
    Process a user query with GraphRAG and save messages.

    This function:
    1. Saves the user's question as a message
    2. Retrieves conversation history
    3. Builds context for GraphRAG
    4. Executes GraphRAG query
    5. Saves the assistant's response with retrieved context
    6. Returns the response with message and graph data

    Args:
        db: Database session.
        conversation_id: Conversation UUID.
        question: User's question.

    Returns:
        dict: Response containing message and retrieved_graph.

    Raises:
        QueryProcessingError: If query processing fails.
    """
    user_message_saved = False
    try:
        # 1. Save user message
        logger.info(f"Processing query for conversation {conversation_id}")
        graph_id, workspace_path = await ensure_conversation_graph_loaded(db, conversation_id)
        await save_message(db, conversation_id, "user", question)
        await db.commit()
        user_message_saved = True

        # 2. Retrieve conversation history (limit to last 3 messages for context)
        all_messages = await get_messages_by_conversation(db, conversation_id)

        # Build history excluding the just-added user message
        conversation_history: ConversationHistory | None = None
        if len(all_messages) > 1:
            conversation_history = ConversationHistory()
            for msg in all_messages[:-1][-3:]:  # Last 3 messages before current
                conversation_history.add_turn(msg["role"], msg["content"])

        # 3. Execute GraphRAG query with history
        logger.info(f"Executing GraphRAG query: {question[:50]}...")
        query_result = await graphrag_service.query(
            question,
            conversation_history,
            search_mode,
            query_chat_provider,
            query_embed_provider,
            graph_id,
            workspace_path,
        )

        answer = query_result.get("answer", "")
        retrieved_entities = query_result.get("retrieved_entities", [])
        retrieved_relationships = query_result.get("retrieved_relationships", [])
        retrieved_sources = query_result.get("retrieved_sources", [])
        search_mode_used = query_result.get("search_mode_used", "local")
        search_mode_reason = query_result.get("search_mode_reason", "")

        # 4. Save assistant response with retrieved context
        assistant_message = await save_message(
            db,
            conversation_id,
            "assistant",
            answer,
            retrieved_entities=retrieved_entities,
            retrieved_relationships=retrieved_relationships,
            retrieved_sources=retrieved_sources,
            search_mode_used=search_mode_used,
            search_mode_reason=search_mode_reason,
        )

        # 5. Commit transaction
        await db.commit()

        # 6. Return formatted response
        return {
            "message": assistant_message,
            "retrieved_graph": {
                "entities": retrieved_entities,
                "relationships": retrieved_relationships,
                "sources": retrieved_sources,
            },
            "search_mode_used": search_mode_used,
            "search_mode_reason": search_mode_reason,
        }

    except GraphRAGError as e:
        await db.rollback()
        logger.error(f"GraphRAG error during query processing: {e}")
        search_mode_used, search_mode_reason = graphrag_service.route_search_mode(
            question,
            search_mode,
        )
        assistant_message = await save_message(
            db,
            conversation_id,
            "assistant",
            (
                "A GraphRAG keresés túl sokáig futott, provider-hibára futott, vagy elérte "
                "a beállított query limitet. Próbáld újra Local módban, rövidebb kérdéssel, "
                "vagy válts másik query chat providerre. "
                f"Technikai részlet: {e}"
            ),
            retrieved_entities=[],
            retrieved_relationships=[],
            retrieved_sources=[],
            search_mode_used=search_mode_used,
            search_mode_reason=search_mode_reason,
        )
        await db.commit()
        return {
            "message": assistant_message,
            "retrieved_graph": {
                "entities": [],
                "relationships": [],
                "sources": [],
            },
            "search_mode_used": search_mode_used,
            "search_mode_reason": search_mode_reason,
        }
    except Exception as e:
        await db.rollback()
        logger.exception("Unexpected error during query processing")
        if not user_message_saved:
            raise QueryProcessingError(f"Failed to process query: {e}") from e

        search_mode_used, search_mode_reason = graphrag_service.route_search_mode(
            question,
            search_mode,
        )
        assistant_message = await save_message(
            db,
            conversation_id,
            "assistant",
            (
                "A lekérdezés váratlan backend hibára futott, ezért nem sikerült GraphRAG "
                "választ generálni. A kérdésedet elmentettem; próbáld újra Source vagy Local "
                "módban. "
                f"Technikai részlet: {e}"
            ),
            retrieved_entities=[],
            retrieved_relationships=[],
            retrieved_sources=[],
            search_mode_used=search_mode_used,
            search_mode_reason=search_mode_reason,
        )
        await db.commit()
        return {
            "message": assistant_message,
            "retrieved_graph": {
                "entities": [],
                "relationships": [],
                "sources": [],
            },
            "search_mode_used": search_mode_used,
            "search_mode_reason": search_mode_reason,
        }
