"""Database initialization script for creating tables."""

import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from app.database import sync_engine  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQL statements for table creation
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
    filename TEXT NOT NULL,
    indexed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'completed',
    entity_count INTEGER,
    relationship_count INTEGER
);
"""

# SQL to check if tables exist
CHECK_TABLES_EXIST = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('conversations', 'messages', 'indexed_documents');
"""

# SQL to get table schemas
GET_TABLE_SCHEMA = """
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = :table_name
ORDER BY ordinal_position;
"""

# SQL to drop tables
DROP_TABLES = """
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS indexed_documents CASCADE;
"""


def check_existing_tables() -> list[str]:
    """Check which tables already exist in the database."""
    with sync_engine.connect() as conn:
        result = conn.execute(text(CHECK_TABLES_EXIST))
        return [row[0] for row in result]


def has_data_in_table(table_name: str) -> bool:
    """Check if a table contains any data."""
    with sync_engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()
        return count > 0 if count else False


def drop_all_tables() -> None:
    """Drop all application tables."""
    logger.info("Dropping all tables...")
    with sync_engine.begin() as conn:
        conn.execute(text(DROP_TABLES))
    logger.info("All tables dropped successfully")


def create_tables() -> None:
    """Create all application tables."""
    logger.info("Creating tables...")
    with sync_engine.begin() as conn:
        conn.execute(text(CREATE_CONVERSATIONS_TABLE))
        logger.info("Created conversations table")

        conn.execute(text(CREATE_MESSAGES_TABLE))
        conn.execute(text(ALTER_MESSAGES_SEARCH_METADATA))
        logger.info("Created messages table")

        conn.execute(text(CREATE_INDEXED_DOCUMENTS_TABLE))
        logger.info("Created indexed_documents table")

    logger.info("All tables created successfully")


def main() -> None:
    """Main initialization logic with user prompts."""
    logger.info("Starting database initialization...")

    try:
        # Check existing tables
        existing_tables = check_existing_tables()

        if not existing_tables:
            logger.info("No tables exist. Creating tables...")
            create_tables()
            logger.info("Database initialization complete!")
            return

        logger.info(f"Found existing tables: {', '.join(existing_tables)}")

        # Check for data in existing tables
        tables_with_data = [table for table in existing_tables if has_data_in_table(table)]

        if tables_with_data:
            logger.warning(f"Tables with data: {', '.join(tables_with_data)}")
            print("\nWARNING: Some tables contain data!")
            print("Choose an option:")
            print("  (c) Create missing tables only (preserve existing data)")
            print("  (d) Drop ALL tables and recreate from scratch (DELETES ALL DATA)")
            print("  (q) Quit without changes")

            choice = input("\nYour choice (c/d/q): ").strip().lower()

            if choice == "d":
                confirm = input("Are you sure? This will DELETE ALL DATA! (yes/no): ")
                if confirm.lower() == "yes":
                    drop_all_tables()
                    create_tables()
                    logger.info("Database recreated from scratch")
                else:
                    logger.info("Operation cancelled")
            elif choice == "c":
                create_tables()
                logger.info("Missing tables created, existing data preserved")
            else:
                logger.info("Operation cancelled")
        else:
            # Tables exist but are empty
            print("\nTables exist but are empty.")
            print("  (r) Recreate tables")
            print("  (k) Keep existing structure")
            print("  (q) Quit")

            choice = input("\nYour choice (r/k/q): ").strip().lower()

            if choice == "r":
                drop_all_tables()
                create_tables()
                logger.info("Tables recreated")
            elif choice == "k":
                logger.info("Keeping existing structure")
            else:
                logger.info("Operation cancelled")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
