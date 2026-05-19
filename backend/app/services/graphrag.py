"""GraphRAG service for document indexing and querying."""

import asyncio
import logging
import math
import os
import re
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import graphrag.api as api
import httpx
import pandas as pd  # type: ignore
from graphrag.config.enums import ModelType
from graphrag.config.load_config import load_config
from graphrag.config.models.language_model_config import LanguageModelConfig
from graphrag.config.models.vector_store_schema_config import VectorStoreSchemaConfig
from graphrag.language_model.manager import ModelManager
from graphrag.query.context_builder.conversation_history import (
    ConversationHistory,
)
from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
from graphrag.query.indexer_adapters import (
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag.query.structured_search.local_search.mixed_context import (
    LocalSearchMixedContext,
)
from graphrag.query.structured_search.local_search.search import LocalSearch
from graphrag.tokenizer.get_tokenizer import get_tokenizer
from graphrag.vector_stores.lancedb import LanceDBVectorStore

from app.config import settings

logger = logging.getLogger(__name__)

GEMINI_MODEL_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
INDEX_PROGRESS_HEARTBEAT_CAP = 75
EXTRACT_GRAPH_PROGRESS_PATTERN = re.compile(r"extract graph progress:\s*(\d+)/(\d+)")
INITIAL_CHUNK_SECONDS_ESTIMATE = 60.0
ProgressCallback = Callable[
    [int, str, int | None, int | None, int | None, int | None],
    None,
]

# Type alias for model provider
ModelProvider = Literal["ollama", "gemini"]


class GraphRAGError(Exception):
    """Base exception for GraphRAG operations."""

    pass


class OllamaConnectionError(GraphRAGError):
    """Exception raised when Ollama is unavailable."""

    pass


class GeminiConfigurationError(GraphRAGError):
    """Exception raised when Gemini configuration is invalid."""

    pass


class IndexingError(GraphRAGError):
    """Exception raised during document indexing."""

    pass


class QueryError(GraphRAGError):
    """Exception raised during query execution."""

    pass


class GraphRAGService:
    """Service for managing GraphRAG operations."""

    def __init__(self):
        """Initialize GraphRAG service."""
        self.graphrag_root = Path(settings.graphrag_root)
        self.input_dir = self.graphrag_root / "input"
        self.output_dir = self.graphrag_root / "output"
        self.cache_dir = self.graphrag_root / "cache"
        self.lancedb_uri = f"{self.graphrag_root}/output/lancedb"

        # Store provider configuration with explicit typing
        self.index_provider: ModelProvider = settings.get_index_provider()
        self.query_provider: ModelProvider = settings.get_query_provider()

        logger.info(f"Model providers - Index: {self.index_provider}, Query: {self.query_provider}")

        # Ensure directories exist
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Set environment variables for GraphRAG indexing based on index provider
        self._set_graphrag_env_vars(self.index_provider)

        # Load GraphRAG configuration
        self.config = load_config(self.graphrag_root)

        # Initialize LLM and embedding models for querying
        self._init_models()

        # Cache for indexed data
        self._entities_cache: list[dict[str, Any]] | None = None
        self._relationships_cache: list[dict[str, Any]] | None = None
        self._entities_objects: list[Any] | None = None
        self._relationships_objects: list[Any] | None = None
        self._reports_objects: list[Any] | None = None
        self._text_units_objects: list[Any] | None = None
        self._last_load_time: datetime | None = None
        self._search_engine: LocalSearch | None = None

    def _set_graphrag_env_vars(self, provider: ModelProvider) -> None:
        """
        Set environment variables for GraphRAG based on provider.

        Args:
            provider: The model provider to configure for.
        """
        os.environ["GRAPHRAG_CHUNK_SIZE"] = str(settings.graphrag_chunk_size)
        os.environ["GRAPHRAG_CHUNK_OVERLAP"] = str(settings.graphrag_chunk_overlap)
        os.environ["GRAPHRAG_REQUEST_TIMEOUT"] = str(settings.graphrag_request_timeout)
        os.environ["GRAPHRAG_CLAIM_EXTRACTION_ENABLED"] = str(
            settings.graphrag_claim_extraction_enabled
        ).lower()

        if provider == "ollama":
            os.environ["GRAPHRAG_API_KEY"] = "ollama"  # Dummy key for Ollama
            os.environ["GRAPHRAG_LLM_MODEL"] = settings.ollama_llm_model
            os.environ["GRAPHRAG_EMBEDDING_MODEL"] = settings.ollama_embed_model
            os.environ["GRAPHRAG_API_BASE"] = settings.ollama_base_url or ""
            os.environ["GRAPHRAG_MODEL_PROVIDER"] = "ollama"
            os.environ["GRAPHRAG_CONCURRENT_REQUESTS"] = str(
                settings.graphrag_concurrent_requests
            )
            os.environ["GRAPHRAG_MAX_RETRIES"] = str(settings.graphrag_max_retries)
            os.environ["GRAPHRAG_MAX_RETRY_WAIT"] = str(settings.graphrag_max_retry_wait)
        elif provider == "gemini":
            os.environ["GRAPHRAG_API_KEY"] = settings.gemini_api_key or ""
            os.environ["GRAPHRAG_LLM_MODEL"] = settings.gemini_llm_model
            os.environ["GRAPHRAG_EMBEDDING_MODEL"] = settings.gemini_embed_model
            os.environ["GRAPHRAG_API_BASE"] = ""  # Empty for Gemini (uses default)
            os.environ["GRAPHRAG_MODEL_PROVIDER"] = "gemini"
            os.environ["GRAPHRAG_CONCURRENT_REQUESTS"] = str(
                settings.graphrag_concurrent_requests
            )
            os.environ["GRAPHRAG_MAX_RETRIES"] = str(settings.graphrag_max_retries)
            os.environ["GRAPHRAG_MAX_RETRY_WAIT"] = str(settings.graphrag_max_retry_wait)

        logger.info(f"GraphRAG environment configured for {provider}")

    def _create_model_config(
        self, provider: ModelProvider, model_type: ModelType
    ) -> LanguageModelConfig:
        """
        Create a LanguageModelConfig for the specified provider and model type.

        Args:
            provider: The model provider ("ollama" or "gemini").
            model_type: The type of model (Chat or Embedding).

        Returns:
            LanguageModelConfig: Configuration for the model.
        """
        if provider == "ollama":
            if model_type == ModelType.Chat:
                return LanguageModelConfig(
                    api_key="ollama",  # Dummy key for Ollama
                    type=ModelType.Chat,
                    model_provider="ollama",
                    model=settings.ollama_llm_model,
                    api_base=settings.ollama_base_url,
                    max_retries=3,
                )
            else:  # Embedding
                return LanguageModelConfig(
                    api_key="ollama",  # Dummy key for Ollama
                    type=ModelType.Embedding,
                    model_provider="ollama",
                    model=settings.ollama_embed_model,
                    api_base=settings.ollama_base_url,
                    max_retries=3,
                )
        elif provider == "gemini":
            if model_type == ModelType.Chat:
                return LanguageModelConfig(
                    api_key=settings.gemini_api_key or "",
                    type=ModelType.Chat,
                    model_provider="gemini",
                    model=settings.gemini_llm_model,
                    max_retries=3,
                )
            else:  # Embedding
                return LanguageModelConfig(
                    api_key=settings.gemini_api_key or "",
                    type=ModelType.Embedding,
                    model_provider="gemini",
                    model=settings.gemini_embed_model,
                    max_retries=3,
                )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _init_models(self) -> None:
        """Initialize LLM and embedding models for querying."""
        # Create model configurations for the query provider
        chat_config = self._create_model_config(self.query_provider, ModelType.Chat)
        embedding_config = self._create_model_config(self.query_provider, ModelType.Embedding)

        # Initialize models for querying
        self.chat_model = ModelManager().get_or_create_chat_model(
            name="local_search_chat",
            model_type=ModelType.Chat,
            config=chat_config,
        )

        self.text_embedder = ModelManager().get_or_create_embedding_model(
            name="local_search_embedding",
            model_type=ModelType.Embedding,
            config=embedding_config,
        )

        self.tokenizer = get_tokenizer(chat_config)

        logger.info(f"Models initialized for query provider: {self.query_provider}")

    async def check_ollama_health(self) -> bool:
        """
        Check if Ollama service is available.

        Returns:
            bool: True if Ollama is available, False otherwise.

        Raises:
            OllamaConnectionError: If Ollama is unavailable.
        """
        if not settings.ollama_base_url:
            logger.warning("Ollama base URL not configured")
            return False

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.ollama_base_url}/api/tags")
                if response.status_code == 200:
                    logger.info("Ollama connection successful")
                    return True
                logger.warning(f"Ollama returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            raise OllamaConnectionError(f"Ollama service unavailable: {e}") from e

    async def check_gemini_health(self) -> bool:
        """
        Check if Gemini API is configured and the selected models exist.

        Returns:
            bool: True if Gemini API key and models are usable.

        Raises:
            GeminiConfigurationError: If Gemini API key or model settings are invalid.
        """
        if not settings.gemini_api_key:
            raise GeminiConfigurationError("Gemini API key not configured")

        await self._verify_gemini_model(settings.gemini_llm_model, "LLM")
        await self._verify_gemini_model(settings.gemini_embed_model, "embedding")

        logger.info("Gemini API key and model settings are valid")
        return True

    async def _verify_gemini_model(self, model: str, model_label: str) -> None:
        """Verify a Gemini model name before starting a long indexing job."""
        model_path = model if model.startswith("models/") else f"models/{model}"
        url = f"{GEMINI_MODEL_API_BASE}/{model_path}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params={"key": settings.gemini_api_key})
        except Exception as e:
            raise GeminiConfigurationError(f"Failed to verify Gemini {model_label} model: {e}") from e

        if response.status_code == 404:
            raise GeminiConfigurationError(
                f"Gemini {model_label} model '{model}' was not found. "
                "Check APP_GEMINI_LLM_MODEL / APP_GEMINI_EMBED_MODEL."
            )

        if response.status_code in {400, 401, 403}:
            raise GeminiConfigurationError(
                f"Gemini rejected {model_label} model verification "
                f"with HTTP {response.status_code}. Check APP_GEMINI_API_KEY and model settings."
            )

        if response.status_code >= 500:
            logger.warning(
                "Gemini %s model verification returned HTTP %s; continuing because this can be temporary.",
                model_label,
                response.status_code,
            )
            return

        response.raise_for_status()

    def _summarize_indexing_error(self, error: Exception) -> str:
        """Return a concise user-facing error for common provider failures."""
        error_text = str(error)

        if "API key expired" in error_text or "API_KEY_INVALID" in error_text:
            return "Gemini API key expired or invalid. Renew APP_GEMINI_API_KEY and restart the backend."

        if (
            settings.get_index_provider() == "ollama"
            and ("Timeout" in error_text or "timed out" in error_text)
        ):
            return (
                "Ollama generation timed out while GraphRAG was extracting entities. "
                "Increase APP_GRAPHRAG_REQUEST_TIMEOUT or reduce APP_GRAPHRAG_CHUNK_SIZE."
            )

        if "404" in error_text or "NOT_FOUND" in error_text:
            return (
                "Gemini model was not found. Check APP_GEMINI_LLM_MODEL; "
                "for Gemini 2.0 Flash-Lite use gemini-2.0-flash-lite."
            )

        if "503" in error_text or "ServiceUnavailableError" in error_text:
            return (
                "Gemini model is temporarily overloaded. Retry later, switch "
                "APP_GEMINI_LLM_MODEL, or use Ollama/local indexing."
            )

        if "RESOURCE_EXHAUSTED" in error_text or "Quota exceeded" in error_text:
            return "Gemini quota exceeded. Wait for the quota reset, use a paid quota, switch to Ollama, or index a smaller sample."

        retry_after = re.search(r"retry in ([^.\n]+)", error_text, flags=re.IGNORECASE)
        if retry_after:
            return f"Gemini quota/rate limit reached. Retry {retry_after.group(1).strip()}."

        if "429" in error_text:
            return "Gemini rate limit reached. Retry later or reduce the input size."

        if "400 Bad Request" in error_text and settings.get_index_provider() == "gemini":
            return "Gemini rejected the indexing request. Check APP_GEMINI_API_KEY and model settings."

        return error_text

    async def check_provider_health(self, provider: ModelProvider | None = None) -> bool:
        """
        Check if the specified (or query) provider is available.

        Args:
            provider: The provider to check. Defaults to query_provider.

        Returns:
            bool: True if provider is available.
        """
        check_provider = provider or self.query_provider

        if check_provider == "ollama":
            return await self.check_ollama_health()
        elif check_provider == "gemini":
            return await self.check_gemini_health()
        return False

    async def verify_models(self) -> dict[str, bool]:
        """
        Verify required models are available for the query provider.

        Returns:
            dict: Model availability status.
        """
        if self.query_provider == "gemini":
            # For Gemini, we just check if API key is configured
            has_key = bool(settings.gemini_api_key)
            return {"llm": has_key, "embedding": has_key}

        # For Ollama, check if models are pulled
        if not settings.ollama_base_url:
            return {"llm": False, "embedding": False}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{settings.ollama_base_url}/api/tags")
                if response.status_code != 200:
                    return {"llm": False, "embedding": False}

                data = response.json()
                available_models = [model["name"] for model in data.get("models", [])]

                llm_available = any(
                    settings.ollama_llm_model in model for model in available_models
                )
                embed_available = any(
                    settings.ollama_embed_model in model for model in available_models
                )

                return {"llm": llm_available, "embedding": embed_available}
        except Exception as e:
            logger.error(f"Failed to verify models: {e}")
            return {"llm": False, "embedding": False}

    async def index_document(
        self,
        filename: str,
        content: bytes,
        progress_callback: ProgressCallback | None = None,
    ) -> dict[str, Any]:
        """
        Index a document with GraphRAG.

        Args:
            filename: Name of the file.
            content: File content as bytes.

        Returns:
            dict: Indexing statistics (entity_count, relationship_count).

        Raises:
            IndexingError: If indexing fails.
        """
        try:
            # Save file to input directory
            if progress_callback:
                progress_callback(
                    10,
                    "Saving document to the GraphRAG input directory",
                    None,
                    None,
                    None,
                    None,
                )

            file_path = self.input_dir / filename
            file_path.write_bytes(content)
            logger.info(f"Saved document to {file_path}")
            estimated_total_chunks = self._estimate_chunk_count(content)
            indexing_log_offset = self._get_indexing_log_offset()

            # Run GraphRAG indexing using Python API
            if progress_callback:
                progress_callback(
                    20,
                    "Starting GraphRAG indexing",
                    0,
                    estimated_total_chunks,
                    1,
                    0,
                )

            logger.info("Starting GraphRAG indexing...")

            async def report_indexing_heartbeat() -> None:
                progress = 20
                chunks_processed = 0
                total_chunks = estimated_total_chunks
                current_chunk = 1
                current_chunk_progress = 0
                last_processed = 0
                chunk_started_at = time.monotonic()
                avg_chunk_seconds: float | None = None
                while True:
                    await asyncio.sleep(5)
                    now = time.monotonic()
                    extract_progress = self._read_extract_graph_progress(indexing_log_offset)
                    if extract_progress:
                        chunks_processed, total_chunks = extract_progress
                        if chunks_processed > last_processed:
                            completed_delta = chunks_processed - last_processed
                            elapsed = max(now - chunk_started_at, 1.0)
                            latest_avg = elapsed / completed_delta
                            avg_chunk_seconds = (
                                latest_avg
                                if avg_chunk_seconds is None
                                else (avg_chunk_seconds * 0.7) + (latest_avg * 0.3)
                            )
                            last_processed = chunks_processed
                            chunk_started_at = now

                        if chunks_processed >= total_chunks:
                            current_chunk = total_chunks
                            current_chunk_progress = 100
                        else:
                            current_chunk = chunks_processed + 1
                            expected_seconds = avg_chunk_seconds or INITIAL_CHUNK_SECONDS_ESTIMATE
                            current_chunk_progress = min(
                                99,
                                math.floor(
                                    100 * (now - chunk_started_at) / max(expected_seconds, 1.0)
                                ),
                            )

                        progress = min(
                            20
                            + math.floor(
                                55
                                * (
                                    chunks_processed
                                    + (current_chunk_progress / 100 if chunks_processed < total_chunks else 0)
                                )
                                / max(total_chunks, 1)
                            ),
                            INDEX_PROGRESS_HEARTBEAT_CAP,
                        )
                        message = (
                            "GraphRAG finished chunk extraction; finalizing graph"
                            if chunks_processed >= total_chunks
                            else "GraphRAG is extracting entities and relationships"
                        )
                    else:
                        current_chunk = 1
                        expected_seconds = avg_chunk_seconds or INITIAL_CHUNK_SECONDS_ESTIMATE
                        current_chunk_progress = min(
                            99,
                            math.floor(
                                100 * (now - chunk_started_at) / max(expected_seconds, 1.0)
                            ),
                        )
                        progress = min(progress + 2, INDEX_PROGRESS_HEARTBEAT_CAP)
                        message = "GraphRAG is preparing chunks for extraction"

                    if progress_callback:
                        progress_callback(
                            progress,
                            message,
                            chunks_processed,
                            total_chunks,
                            current_chunk,
                            current_chunk_progress,
                        )

            heartbeat_task = asyncio.create_task(report_indexing_heartbeat())
            try:
                index_result = await asyncio.wait_for(
                    api.build_index(config=self.config),
                    timeout=settings.graphrag_index_timeout_seconds,
                )
            finally:
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass

            # Check for errors
            errors = []
            for workflow_result in index_result:
                if workflow_result.errors:
                    errors.append(f"{workflow_result.workflow}: {workflow_result.errors}")

            if errors:
                error_msg = "; ".join(errors)
                logger.error(f"GraphRAG indexing failed: {error_msg}")
                raise IndexingError(f"Indexing failed: {error_msg}")

            logger.info("GraphRAG indexing completed successfully")
            if progress_callback:
                latest_progress = self._read_extract_graph_progress(indexing_log_offset)
                if latest_progress:
                    chunks_processed, total_chunks = latest_progress
                else:
                    chunks_processed = estimated_total_chunks
                    total_chunks = estimated_total_chunks
                progress_callback(
                    95,
                    "Loading indexed graph statistics",
                    chunks_processed,
                    total_chunks,
                    total_chunks,
                    100,
                )

            # Invalidate all caches
            self._entities_cache = None
            self._relationships_cache = None
            self._entities_objects = None
            self._relationships_objects = None
            self._reports_objects = None
            self._text_units_objects = None
            self._search_engine = None

            # Load and count entities/relationships
            stats = self._count_indexed_data()
            if progress_callback:
                progress_callback(
                    100,
                    "Indexing completed",
                    total_chunks,
                    total_chunks,
                    total_chunks,
                    100,
                )
            return stats

        except TimeoutError as e:
            message = (
                f"Indexing timed out after {settings.graphrag_index_timeout_seconds // 60} minutes. "
                "Use a smaller text file or a provider with higher quota."
            )
            logger.error(message)
            raise IndexingError(message) from e
        except Exception as e:
            message = self._summarize_indexing_error(e)
            logger.error(f"Failed to index document: {message}")
            raise IndexingError(message) from e

    def _estimate_chunk_count(self, content: bytes) -> int:
        """Estimate GraphRAG text-unit count before the chunking workflow finishes."""
        text = content.decode("utf-8", errors="ignore")
        try:
            token_count = len(self.tokenizer.encode(text))
        except Exception:
            token_count = max(1, math.ceil(len(text.split()) * 1.33))

        chunk_size = max(settings.graphrag_chunk_size, 1)
        overlap = min(max(settings.graphrag_chunk_overlap, 0), chunk_size - 1)
        stride = max(chunk_size - overlap, 1)

        if token_count <= chunk_size:
            return 1

        return max(1, math.ceil((token_count - overlap) / stride))

    def _get_indexing_log_offset(self) -> int:
        """Return the current GraphRAG log size so progress parsing ignores old runs."""
        log_path = self.output_dir / "indexing-engine.log"
        try:
            return log_path.stat().st_size
        except FileNotFoundError:
            return 0

    def _read_extract_graph_progress(self, log_offset: int) -> tuple[int, int] | None:
        """Read GraphRAG's latest extract_graph chunk progress from the current run log."""
        log_path = self.output_dir / "indexing-engine.log"
        try:
            with log_path.open("r", encoding="utf-8", errors="ignore") as log_file:
                log_file.seek(log_offset)
                content = log_file.read()
        except FileNotFoundError:
            return None

        matches = EXTRACT_GRAPH_PROGRESS_PATTERN.findall(content)
        if not matches:
            return None

        processed, total = matches[-1]
        return int(processed), int(total)

    def _count_indexed_data(self) -> dict[str, int]:
        """
        Count entities and relationships from indexed data.

        Returns:
            dict: Counts of entities and relationships.
        """
        try:
            entities = self._load_entities()
            relationships = self._load_relationships()

            return {
                "entity_count": len(entities) if entities else 0,
                "relationship_count": len(relationships) if relationships else 0,
            }
        except Exception as e:
            logger.warning(f"Failed to count indexed data: {e}")
            return {"entity_count": 0, "relationship_count": 0}

    def _load_indexed_data_objects(self) -> None:
        """Load indexed data as GraphRAG objects for querying."""
        if self._entities_objects is not None:
            return

        try:
            # Load parquet files
            entity_df = pd.read_parquet(f"{self.output_dir}/entities.parquet")
            community_df = pd.read_parquet(f"{self.output_dir}/communities.parquet")
            relationship_df = pd.read_parquet(f"{self.output_dir}/relationships.parquet")
            report_df = pd.read_parquet(f"{self.output_dir}/community_reports.parquet")
            text_unit_df = pd.read_parquet(f"{self.output_dir}/text_units.parquet")

            # Convert to GraphRAG objects
            self._entities_objects = read_indexer_entities(entity_df, community_df, 2)
            self._relationships_objects = read_indexer_relationships(relationship_df)
            self._reports_objects = read_indexer_reports(report_df, community_df, 2)
            self._text_units_objects = read_indexer_text_units(text_unit_df)

            logger.info(
                f"Loaded {len(self._entities_objects)} entities, "
                f"{len(self._relationships_objects)} relationships, "
                f"{len(self._reports_objects)} reports, "
                f"{len(self._text_units_objects)} text units"
            )
        except Exception as e:
            logger.error(f"Failed to load indexed data objects: {e}")
            self._entities_objects = []
            self._relationships_objects = []
            self._reports_objects = []
            self._text_units_objects = []

    def _load_entities(self) -> list[dict[str, Any]]:
        """
        Load entities from GraphRAG output.

        Returns:
            list: List of entity dictionaries.
        """
        if self._entities_cache is not None:
            return self._entities_cache

        entities_file = self.output_dir / "entities.parquet"

        if not entities_file.exists():
            logger.warning(f"Entities file not found: {entities_file}")
            return []

        try:
            df = pd.read_parquet(entities_file)
            entities: list[dict[str, Any]] = df.to_dict("records")  # type: ignore
            self._entities_cache = entities
            self._last_load_time = datetime.utcnow()
            logger.info(f"Loaded {len(entities)} entities from GraphRAG output")
            return entities
        except Exception as e:
            logger.error(f"Failed to load entities: {e}")
            return []

    def _load_relationships(self) -> list[dict[str, Any]]:
        """
        Load relationships from GraphRAG output.

        Returns:
            list: List of relationship dictionaries.
        """
        if self._relationships_cache is not None:
            return self._relationships_cache

        relationships_file = self.output_dir / "relationships.parquet"

        if not relationships_file.exists():
            logger.warning(f"Relationships file not found: {relationships_file}")
            return []

        try:
            df = pd.read_parquet(relationships_file)
            relationships: list[dict[str, Any]] = df.to_dict("records")  # type: ignore
            self._relationships_cache = relationships
            logger.info(f"Loaded {len(relationships)} relationships from GraphRAG output")
            return relationships
        except Exception as e:
            logger.error(f"Failed to load relationships: {e}")
            return []

    async def query(
        self, question: str, conversation_history: ConversationHistory | None = None
    ) -> dict[str, Any]:
        """
        Execute a query against the indexed knowledge graph.

        Args:
            question: User question.
            conversation_history: Previous conversation messages.

        Returns:
            dict: Query response with answer and retrieved context.

        Raises:
            QueryError: If query execution fails.
        """
        try:
            # Load indexed data objects
            self._load_indexed_data_objects()

            # Initialize search engine if needed
            if self._search_engine is None:
                self._search_engine = self._create_search_engine()

            # Execute search (conversation history will be added later)
            logger.info(f"Executing GraphRAG query: {question[:50]}...")
            result = await self._search_engine.search(
                query=question, conversation_history=conversation_history
            )

            logger.info("GraphRAG query completed successfully")

            # Extract retrieved entities and relationships from context_data
            retrieved_entities: list = []
            retrieved_relationships: list = []

            if hasattr(result, "context_data"):
                try:
                    context_data_dict = result.context_data
                    if isinstance(context_data_dict, dict):
                        # Log ALL keys in context_data to see what's available
                        logger.info(f"Context data keys: {list(context_data_dict.keys())}")

                        # Log details of each DataFrame
                        for key, value in context_data_dict.items():
                            if hasattr(value, "columns"):
                                logger.info(f"{key} DataFrame shape: {value.shape}")
                                if not value.empty:
                                    logger.info(
                                        f"{key} DataFrame columns: {value.columns.tolist()}"
                                    )
                                    if "id" in value.columns:
                                        logger.info(f"{key} IDs: {value['id'].tolist()}")
                                    # Log full DataFrame content for sources to see citation numbers
                                    if key == "sources":
                                        logger.info(
                                            f"Sources DataFrame full content:\n{value.to_string()}"
                                        )

                        # Get entities used in context
                        entities_df = context_data_dict.get("entities")
                        if (
                            entities_df is not None
                            and hasattr(entities_df, "empty")
                            and not entities_df.empty
                        ):
                            # Filter only entities that were included in context
                            if "in_context" in entities_df.columns:
                                entities_in_context = entities_df[entities_df["in_context"] == True]  # noqa: E712
                            else:
                                entities_in_context = entities_df

                            # Log available columns for debugging
                            logger.info(
                                f"Entity DataFrame columns: {entities_in_context.columns.tolist()}"
                            )
                            logger.info(
                                f"Entity DataFrame index: {entities_in_context.index.tolist()}"
                            )
                            logger.info(
                                f"Entity IDs from 'id' column: {entities_in_context['id'].tolist()}"
                            )

                            # Convert to serializable format with proper field names
                            # Use the 'id' column value as the citation index (this is what GraphRAG uses in "Sources (X)")
                            retrieved_entities = []
                            for _, row in entities_in_context.iterrows():
                                # The 'id' column contains the citation number (e.g., 7, 11, 14)
                                citation_id = row.get("id", None)
                                entity_dict = {
                                    "id": str(citation_id) if citation_id is not None else "",
                                    "title": str(
                                        row.get("entity", "")
                                    ),  # 'entity' column contains the name
                                    "type": "entity",  # Type not available in this DataFrame
                                    "description": str(row.get("description", "")),
                                    "rank": row.get("number of relationships", 0),
                                    # Use the 'id' column as the citation index
                                    "index": int(citation_id)
                                    if citation_id is not None
                                    and isinstance(citation_id, (int, float, str))
                                    else None,
                                }
                                retrieved_entities.append(
                                    self._convert_to_serializable(entity_dict)
                                )

                        # Get relationships used in context
                        rels_df = context_data_dict.get("relationships")
                        if rels_df is not None and hasattr(rels_df, "empty") and not rels_df.empty:
                            # Filter only relationships that were included in context
                            if "in_context" in rels_df.columns:
                                rels_in_context = rels_df[rels_df["in_context"] == True]  # noqa: E712
                            else:
                                rels_in_context = rels_df

                            # Log available columns for debugging
                            logger.info(
                                f"Relationship DataFrame columns: {rels_in_context.columns.tolist()}"
                            )
                            logger.info(
                                f"Relationship DataFrame index: {rels_in_context.index.tolist()}"
                            )
                            logger.info(
                                f"Relationship IDs from 'id' column: {rels_in_context['id'].tolist()}"
                            )

                            # Convert to serializable format with proper field names
                            # Use the 'id' column value as the citation index
                            retrieved_relationships = []
                            for _, row in rels_in_context.iterrows():
                                # The 'id' column contains the citation number
                                citation_id = row.get("id", None)
                                rel_dict = {
                                    "id": str(citation_id) if citation_id is not None else "",
                                    "source": str(row.get("source", "")),
                                    "target": str(row.get("target", "")),
                                    "description": str(row.get("description", "")),
                                    "weight": float(row.get("weight", 1.0)),
                                    # Use the 'id' column as the citation index
                                    "index": int(citation_id)
                                    if citation_id is not None
                                    and isinstance(citation_id, (int, float, str))
                                    else None,
                                }
                                retrieved_relationships.append(
                                    self._convert_to_serializable(rel_dict)
                                )
                except Exception as e:
                    logger.warning(f"Failed to extract context data: {e}")

            return {
                "answer": result.response,
                "retrieved_entities": retrieved_entities,
                "retrieved_relationships": retrieved_relationships,
            }

        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise QueryError(f"Failed to execute query: {e}") from e

    def _create_search_engine(self) -> LocalSearch:
        """Create and configure local search engine."""
        try:
            # Ensure data objects are loaded and not None
            if not self._entities_objects:
                raise QueryError("No entities loaded - index may be empty")

            # Initialize vector store for entity embeddings
            description_embedding_store = LanceDBVectorStore(
                vector_store_schema_config=VectorStoreSchemaConfig(
                    index_name="default-entity-description"
                )
            )
            description_embedding_store.connect(db_uri=self.lancedb_uri)

            # Create context builder
            context_builder = LocalSearchMixedContext(
                community_reports=self._reports_objects or [],
                text_units=self._text_units_objects or [],
                entities=self._entities_objects or [],
                relationships=self._relationships_objects or [],
                covariates=None,  # Not using covariates
                entity_text_embeddings=description_embedding_store,
                embedding_vectorstore_key=EntityVectorStoreKey.ID,
                text_embedder=self.text_embedder,
                tokenizer=self.tokenizer,
            )
            # Custom system prompt that instructs LLM to cite by entity names and relationship pairs
            custom_system_prompt = """
---Role---

You are a helpful assistant responding to questions about data in the tables provided.


---Goal---

Generate a response of the target length and format that responds to the user's question,
 summarizing all information in the input data tables appropriate for the response length
 and format, and incorporating any relevant general knowledge.

If you don't know the answer, just say so. Do not make anything up.

Points supported by data should list their data references as follows:

"This is an example sentence supported by data [
    Data: Entities (ENTITY_NAME, ANOTHER_ENTITY);
    Relationships (SOURCE_ENTITY, TARGET_ENTITY)
]."

**Important citation rules:**
- Only cite entities and relationships that are actually mentioned in the data tables below
- Use the exact entity names as they appear in the Entities table
- For relationships, use the exact source and target names from the Relationships table
- Only add citations when the information directly comes from the provided data
- Do not cite if you're using general knowledge


---Target response length and format---

{response_type}


---Data tables---

{context_data}


---Goal---

Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format.

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.
"""

            # Create search engine
            # Note: text_unit_prop and community_prop control token allocation in the context window.
            # text_unit_prop (0.5) allocates 50% of tokens to raw text chunks for detailed, specific answers.
            # community_prop (0.1) allocates 10% to high-level community summaries for broader understanding.
            # The remaining ~40% goes to entities and relationships from the knowledge graph.
            search_engine = LocalSearch(
                model=self.chat_model,
                context_builder=context_builder,
                tokenizer=self.tokenizer,
                system_prompt=custom_system_prompt,
                model_params={
                    "max_tokens": 2000,
                    "temperature": 0.0,
                },
                context_builder_params={
                    "text_unit_prop": 0.5,
                    "community_prop": 0.1,
                    "conversation_history_max_turns": 3,
                    "conversation_history_user_turns_only": True,
                    "top_k_mapped_entities": 10,
                    "top_k_relationships": 10,
                    "include_entity_rank": True,
                    "include_relationship_weight": True,
                    "include_community_rank": False,
                    "return_candidate_context": False,
                    "embedding_vectorstore_key": EntityVectorStoreKey.ID,
                    "max_tokens": 12000,
                },
                response_type="multiple paragraphs",
            )

            logger.info("Search engine initialized successfully")
            return search_engine

        except Exception as e:
            logger.error(f"Failed to create search engine: {e}")
            raise QueryError(f"Failed to initialize search engine: {e}") from e

    def get_full_graph(self) -> dict[str, Any]:
        """
        Get the full knowledge graph in React Flow format.

        Returns:
            dict: Graph data with nodes and edges.
        """
        entities = self._load_entities()
        relationships = self._load_relationships()

        nodes, duplicate_entity_count = self._transform_entities_to_nodes(entities)
        edges, graph_nodes, cleanup_stats = self._transform_relationships_to_edges(
            relationships,
            nodes,
        )
        metadata = self._annotate_graph_components(graph_nodes, edges)
        metadata.update(cleanup_stats)
        metadata["duplicate_entity_count"] = duplicate_entity_count

        return {"nodes": graph_nodes, "edges": edges, "metadata": metadata}

    def _convert_to_serializable(self, obj: Any) -> Any:
        """
        Convert numpy and pandas types to JSON-serializable Python types.

        Args:
            obj: Object to convert.

        Returns:
            JSON-serializable object.
        """
        import numpy as np

        if isinstance(obj, dict):
            return {k: self._convert_to_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if pd.isna(obj):
            return None
        return obj

    def _normalize_entity_key(self, value: Any) -> str:
        """Normalize entity labels for exact matching without changing display text."""
        text = str(value or "").strip().strip('"').strip("'")
        text = text.replace("’", "'")
        text = re.sub(r"[^\w\s]", " ", text.casefold(), flags=re.UNICODE)
        return re.sub(r"\s+", " ", text).strip()

    def _compact_entity_key(self, value: Any) -> str:
        """Return an alphanumeric-only key for punctuation-insensitive endpoint matching."""
        return re.sub(r"[^\w]", "", self._normalize_entity_key(value), flags=re.UNICODE)

    def _has_valid_coordinate(self, value: Any) -> bool:
        """Return True when a GraphRAG coordinate can be used for rendering."""
        return value is not None and not (isinstance(value, float) and pd.isna(value))

    def _fallback_node_position(self, index: int, total: int) -> dict[str, float]:
        """Place nodes without GraphRAG coordinates in a deterministic outer ring."""
        angle = (2 * math.pi * index) / max(total, 1)
        radius = 250 + (index % 3) * 80
        return {
            "x": float(math.cos(angle) * radius + 500),
            "y": float(math.sin(angle) * radius + 400),
        }

    def _transform_entities_to_nodes(
        self, entities: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], int]:
        """
        Transform entities to React Flow nodes.

        Args:
            entities: List of entity dictionaries.

        Returns:
            tuple: List of node dictionaries and duplicate entity count.
        """
        nodes: list[dict[str, Any]] = []
        node_by_key: dict[str, dict[str, Any]] = {}
        canonical_key_by_entity_key = self._build_entity_canonical_key_map(entities)
        title_by_key = {
            self._normalize_entity_key(entity.get("title", entity.get("name", ""))): str(
                entity.get("title", entity.get("name", "Unknown"))
            )
            for entity in entities
        }
        duplicate_entity_count = 0

        for idx, entity in enumerate(entities):
            # Extract entity properties - GraphRAG uses 'title' not 'name'
            title = entity.get("title", entity.get("name", "Unknown"))
            normalized_title = self._normalize_entity_key(title)
            if not normalized_title:
                continue

            canonical_key = canonical_key_by_entity_key.get(normalized_title, normalized_title)
            canonical_title = title_by_key.get(canonical_key, str(title))

            existing_node = node_by_key.get(canonical_key)
            if existing_node:
                duplicate_entity_count += 1
                aliases = existing_node["data"].setdefault("aliases", [])
                if title != existing_node["data"]["label"] and title not in aliases:
                    aliases.append(title)

                if description := entity.get("description", ""):
                    existing_description = existing_node["data"].get("description") or ""
                    if len(str(description)) > len(str(existing_description)):
                        existing_node["data"]["description"] = description

                merged_entities = existing_node["data"]["properties"].setdefault(
                    "merged_entities",
                    [],
                )
                merged_entities.append(self._convert_to_serializable(entity))
                continue

            # Use title as ID for matching with relationships
            entity_id = str(canonical_title)
            description = entity.get("description", "")
            entity_type = entity.get("type", "entity")

            # Use entity positions from GraphRAG layout algorithm
            x = entity.get("x", None)
            y = entity.get("y", None)

            # Convert numpy types to Python native types for JSON serialization
            if hasattr(x, "item"):  # numpy scalar
                x = x.item()  # type: ignore
            if hasattr(y, "item"):  # numpy scalar
                y = y.item()  # type: ignore

            # Check if we have valid GraphRAG coordinates
            has_valid_x = self._has_valid_coordinate(x)
            has_valid_y = self._has_valid_coordinate(y)

            if has_valid_x and has_valid_y:
                # Scale GraphRAG coordinates (usually -1 to 1) to pixel space
                # Smaller scale to keep graph compact and visible
                x = x * 600 + 500  # type: ignore
                y = y * 450 + 400  # type: ignore
                position = {"x": float(x), "y": float(y)}
            else:
                position = self._fallback_node_position(idx, len(entities))

            # Convert entity dict to JSON-serializable format
            serializable_entity = self._convert_to_serializable(entity)

            node = {
                "id": entity_id,
                "data": {
                    "label": canonical_title,
                    "type": entity_type,
                    "description": description,
                    "properties": serializable_entity,
                    "aliases": [title] if title != canonical_title else [],
                    "degree": 0,
                    "component_id": None,
                    "is_isolated": False,
                    "is_in_largest_component": False,
                    "generated_from_relationship": False,
                },
                "position": position,
                "type": "custom",
            }
            nodes.append(node)
            node_by_key[canonical_key] = node

        return nodes, duplicate_entity_count

    def _build_entity_canonical_key_map(
        self,
        entities: list[dict[str, Any]],
    ) -> dict[str, str]:
        """Find conservative aliases such as EINSTEIN -> ALBERT EINSTEIN."""
        title_keys: dict[str, str] = {}
        for entity in entities:
            title = entity.get("title", entity.get("name", ""))
            key = self._normalize_entity_key(title)
            if key:
                title_keys[key] = str(title)

        canonical_key_by_entity_key: dict[str, str] = {}
        for entity in entities:
            title = entity.get("title", entity.get("name", ""))
            key = self._normalize_entity_key(title)
            if not key:
                continue

            words = key.split()
            entity_type = str(entity.get("type", "")).casefold()
            if len(words) != 1 or entity_type != "person":
                continue

            description_key = self._normalize_entity_key(entity.get("description", ""))
            candidates = [
                candidate_key
                for candidate_key in title_keys
                if candidate_key != key
                and candidate_key.endswith(f" {key}")
                and len(candidate_key.split()) >= 2
                and candidate_key in description_key
            ]

            if len(candidates) == 1:
                canonical_key_by_entity_key[key] = candidates[0]

        return canonical_key_by_entity_key

    def _transform_relationships_to_edges(
        self,
        relationships: list[dict[str, Any]],
        nodes: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
        """
        Transform relationships to React Flow edges.

        Args:
            relationships: List of relationship dictionaries.
            nodes: List of known entity nodes.

        Returns:
            tuple: List of edge dictionaries, updated nodes, and cleanup stats.
        """
        graph_nodes = list(nodes)
        node_by_id = {node["id"]: node for node in graph_nodes}
        endpoint_matches = self._build_endpoint_match_index(graph_nodes)

        edges = []
        relationship_only_node_count = 0
        unresolved_relationship_count = 0
        endpoint_alias_match_count = 0
        self_loop_edge_count = 0

        for idx, rel in enumerate(relationships):
            source = str(rel.get("source", ""))
            target = str(rel.get("target", ""))
            description = rel.get("description", "")
            weight = rel.get("weight", 1.0)

            # Convert numpy types to Python native types
            if hasattr(weight, "item"):
                weight = weight.item()

            # Convert relationship dict to JSON-serializable format
            serializable_rel = self._convert_to_serializable(rel)

            if not source or not target:
                unresolved_relationship_count += 1
                continue

            resolved_source, source_was_alias = self._resolve_endpoint(
                source,
                endpoint_matches,
                graph_nodes,
            )
            resolved_target, target_was_alias = self._resolve_endpoint(
                target,
                endpoint_matches,
                graph_nodes,
            )
            endpoint_alias_match_count += int(source_was_alias) + int(target_was_alias)

            if not resolved_source:
                resolved_source = source
                created = self._create_relationship_endpoint_node(
                    source,
                    len(graph_nodes),
                    len(nodes) + len(relationships),
                )
                graph_nodes.append(created)
                node_by_id[created["id"]] = created
                relationship_only_node_count += 1
                endpoint_matches = self._build_endpoint_match_index(graph_nodes)

            if not resolved_target:
                resolved_target = target
                created = self._create_relationship_endpoint_node(
                    target,
                    len(graph_nodes),
                    len(nodes) + len(relationships),
                )
                graph_nodes.append(created)
                node_by_id[created["id"]] = created
                relationship_only_node_count += 1
                endpoint_matches = self._build_endpoint_match_index(graph_nodes)

            if resolved_source == resolved_target:
                self_loop_edge_count += 1
                continue

            if resolved_source not in node_by_id or resolved_target not in node_by_id:
                unresolved_relationship_count += 1
                continue

            endpoint_resolved = resolved_source != source or resolved_target != target
            edges.append(
                {
                    "id": f"{resolved_source}-{resolved_target}-{idx}",
                    "source": resolved_source,
                    "target": resolved_target,
                    "label": description,
                    "data": {
                        "weight": float(weight),
                        "properties": serializable_rel,
                        "original_source": source,
                        "original_target": target,
                        "endpoint_resolved": endpoint_resolved,
                    },
                }
            )

        return edges, graph_nodes, {
            "relationship_only_node_count": relationship_only_node_count,
            "unresolved_relationship_count": unresolved_relationship_count,
            "endpoint_alias_match_count": endpoint_alias_match_count,
            "self_loop_edge_count": self_loop_edge_count,
        }

    def _build_endpoint_match_index(
        self,
        nodes: list[dict[str, Any]],
    ) -> dict[str, dict[str, str | None]]:
        """Build exact and punctuation-insensitive lookup tables for node labels."""
        normalized: dict[str, str | None] = {}
        compact: dict[str, str | None] = {}

        for node in nodes:
            label = node["data"]["label"]
            for value in [label, *node["data"].get("aliases", [])]:
                normalized_key = self._normalize_entity_key(value)
                compact_key = self._compact_entity_key(value)

                if normalized_key:
                    current = normalized.get(normalized_key)
                    normalized[normalized_key] = (
                        node["id"]
                        if current is None and normalized_key not in normalized
                        else current
                        if current == node["id"]
                        else None
                    )
                if compact_key:
                    current = compact.get(compact_key)
                    compact[compact_key] = (
                        node["id"]
                        if current is None and compact_key not in compact
                        else current
                        if current == node["id"]
                        else None
                    )

        return {"normalized": normalized, "compact": compact}

    def _resolve_endpoint(
        self,
        endpoint: str,
        endpoint_matches: dict[str, dict[str, str | None]],
        nodes: list[dict[str, Any]],
    ) -> tuple[str | None, bool]:
        """Resolve a relationship endpoint to an existing node without over-merging."""
        normalized_key = self._normalize_entity_key(endpoint)
        compact_key = self._compact_entity_key(endpoint)

        exact_match = endpoint_matches["normalized"].get(normalized_key)
        if exact_match:
            return exact_match, exact_match != endpoint

        compact_match = endpoint_matches["compact"].get(compact_key)
        if compact_match:
            return compact_match, compact_match != endpoint

        if len(normalized_key) < 4:
            return None, False

        padded_endpoint = f" {normalized_key} "
        candidates = []
        for node in nodes:
            label_key = self._normalize_entity_key(node["data"]["label"])
            padded_label = f" {label_key} "
            if padded_endpoint in padded_label or label_key.endswith(f" {normalized_key}"):
                candidates.append(node["id"])

        unique_candidates = sorted(set(candidates))
        if len(unique_candidates) == 1:
            return unique_candidates[0], True

        return None, False

    def _create_relationship_endpoint_node(
        self,
        label: str,
        index: int,
        total: int,
    ) -> dict[str, Any]:
        """Create a node for a relationship endpoint missing from entities.parquet."""
        return {
            "id": label,
            "data": {
                "label": label,
                "type": "entity",
                "description": "Mentioned in a relationship but missing from the entity table.",
                "properties": {"source": "relationships.parquet"},
                "aliases": [],
                "degree": 0,
                "component_id": None,
                "is_isolated": False,
                "is_in_largest_component": False,
                "generated_from_relationship": True,
            },
            "position": self._fallback_node_position(index, total),
            "type": "custom",
        }

    def _annotate_graph_components(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Annotate nodes with degree and connected-component metadata."""
        node_ids = {node["id"] for node in nodes}
        adjacency = {node_id: set() for node_id in node_ids}

        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            if source in node_ids and target in node_ids:
                adjacency[source].add(target)
                adjacency[target].add(source)

        components: list[list[str]] = []
        seen: set[str] = set()
        for node_id in node_ids:
            if node_id in seen:
                continue

            stack = [node_id]
            seen.add(node_id)
            component = []
            while stack:
                current = stack.pop()
                component.append(current)
                for neighbor in adjacency[current]:
                    if neighbor not in seen:
                        seen.add(neighbor)
                        stack.append(neighbor)
            components.append(component)

        components.sort(key=len, reverse=True)
        component_by_node: dict[str, int] = {}
        for component_id, component in enumerate(components):
            for node_id in component:
                component_by_node[node_id] = component_id

        largest_component_id = 0 if components else None
        largest_component_node_count = len(components[0]) if components else 0
        isolated_node_count = 0

        for node in nodes:
            node_id = node["id"]
            degree = len(adjacency[node_id])
            component_id = component_by_node.get(node_id)
            is_isolated = degree == 0
            isolated_node_count += int(is_isolated)

            node["data"]["degree"] = degree
            node["data"]["component_id"] = component_id
            node["data"]["is_isolated"] = is_isolated
            node["data"]["is_in_largest_component"] = (
                component_id == largest_component_id and not is_isolated
            )

        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "connected_node_count": len(nodes) - isolated_node_count,
            "isolated_node_count": isolated_node_count,
            "component_count": len(components),
            "largest_component_id": largest_component_id,
            "largest_component_node_count": largest_component_node_count,
            "component_sizes": [len(component) for component in components[:20]],
        }

    def get_stats(self) -> dict[str, Any]:
        """
        Get indexing statistics.

        Returns:
            dict: Statistics about indexed data.
        """
        entities = self._load_entities()
        relationships = self._load_relationships()

        return {
            "entity_count": len(entities) if entities else 0,
            "relationship_count": len(relationships) if relationships else 0,
            "indexed": len(entities) > 0 or len(relationships) > 0,
            "last_indexed_at": (self._last_load_time.isoformat() if self._last_load_time else None),
        }


# Global service instance
graphrag_service = GraphRAGService()
