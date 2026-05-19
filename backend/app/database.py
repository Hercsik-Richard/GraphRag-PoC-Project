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

CREATE_CONVERSATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_MESSAGES_TABLE = """
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    retrieved_entities JSON,
    retrieved_relationships JSON
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
ON messages(conversation_id, created_at);
"""

CREATE_INDEXED_DOCUMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS indexed_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    indexed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'completed',
    entity_count INTEGER,
    relationship_count INTEGER
);
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
        await conn.execute(text(CREATE_CONVERSATIONS_TABLE))
        await conn.execute(text(CREATE_MESSAGES_TABLE))
        await conn.execute(text(CREATE_INDEXED_DOCUMENTS_TABLE))
    logger.info("Database schema is ready")


# Synchronous engine for initialization scripts
sync_engine = create_engine(
    str(settings.database_url).replace("postgresql://", "postgresql+psycopg://"),
    echo=settings.debug,
)
