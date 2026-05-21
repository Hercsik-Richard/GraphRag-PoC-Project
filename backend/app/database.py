"""Database connection management using SQLAlchemy Core."""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

logger = logging.getLogger(__name__)

CREATE_INDEXED_GRAPHS_TABLE = """
CREATE TABLE IF NOT EXISTS indexed_graphs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    source_filename TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'queued',
    entity_count INTEGER,
    relationship_count INTEGER,
    index_chat_provider VARCHAR(20),
    index_embed_provider VARCHAR(20),
    index_chat_model TEXT,
    index_embed_model TEXT,
    workspace_path TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    indexed_at TIMESTAMP,
    activated_at TIMESTAMP,
    error TEXT
);

CREATE INDEX IF NOT EXISTS idx_indexed_graphs_status_created
ON indexed_graphs(status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_indexed_graphs_active
ON indexed_graphs(is_active)
WHERE is_active = TRUE;
"""

CREATE_CONVERSATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    graph_id UUID REFERENCES indexed_graphs(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

ALTER_CONVERSATIONS_GRAPH = """
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS graph_id UUID REFERENCES indexed_graphs(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_conversations_graph_updated
ON conversations(graph_id, updated_at DESC);
"""

CREATE_MESSAGES_TABLE = """
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    retrieved_entities JSON,
    retrieved_relationships JSON,
    retrieved_sources JSON,
    search_mode_used VARCHAR(20),
    search_mode_reason TEXT
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
ON messages(conversation_id, created_at);
"""

ALTER_MESSAGES_SEARCH_METADATA = """
ALTER TABLE messages ADD COLUMN IF NOT EXISTS search_mode_used VARCHAR(20);
ALTER TABLE messages ADD COLUMN IF NOT EXISTS search_mode_reason TEXT;
ALTER TABLE messages ADD COLUMN IF NOT EXISTS retrieved_sources JSON;
"""

CREATE_INDEXED_DOCUMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS indexed_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    graph_id UUID REFERENCES indexed_graphs(id) ON DELETE SET NULL,
    filename TEXT NOT NULL,
    indexed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'completed',
    entity_count INTEGER,
    relationship_count INTEGER
);
"""

ALTER_INDEXED_DOCUMENTS_GRAPH = """
ALTER TABLE indexed_documents ADD COLUMN IF NOT EXISTS graph_id UUID REFERENCES indexed_graphs(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_indexed_documents_graph
ON indexed_documents(graph_id);
"""

# Convert PostgresDsn to string and replace postgresql:// with postgresql+psycopg://
DATABASE_URL = str(settings.database_url).replace("postgresql://", "postgresql+psycopg://")

# Create async engine
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Create async session factory
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """
    Dependency that provides a database session.

    Yields:
        AsyncSession: Database session for the request.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        bool: True if connection is successful, False otherwise.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


async def ensure_database_schema() -> None:
    """Create required application tables if they are missing."""
    async with engine.begin() as conn:
        await conn.execute(text(CREATE_INDEXED_GRAPHS_TABLE))
        await conn.execute(text(CREATE_CONVERSATIONS_TABLE))
        await conn.execute(text(ALTER_CONVERSATIONS_GRAPH))
        await conn.execute(text(CREATE_MESSAGES_TABLE))
        await conn.execute(text(ALTER_MESSAGES_SEARCH_METADATA))
        await conn.execute(text(CREATE_INDEXED_DOCUMENTS_TABLE))
        await conn.execute(text(ALTER_INDEXED_DOCUMENTS_GRAPH))
    logger.info("Database schema is ready")


# Synchronous engine for initialization scripts
sync_engine = create_engine(
    str(settings.database_url).replace("postgresql://", "postgresql+psycopg://"),
    echo=settings.debug,
)
