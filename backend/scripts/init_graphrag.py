"""Initialize GraphRAG workspace directories and configuration."""

import logging
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import chat_temperature_for_model, settings  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SETTINGS_YAML_CONTENT = """# GraphRAG Configuration

encoding_model: cl100k_base

models:
  default_chat_model:
    type: chat
    model_provider: ${GRAPHRAG_CHAT_MODEL_PROVIDER}
    model: ${GRAPHRAG_CHAT_MODEL}
    api_base: ${GRAPHRAG_CHAT_API_BASE}
    api_key: ${GRAPHRAG_CHAT_API_KEY}
    encoding_model: cl100k_base
    max_tokens: 4000
    temperature: ${GRAPHRAG_CHAT_TEMPERATURE}
    top_p: 1
    request_timeout: ${GRAPHRAG_REQUEST_TIMEOUT}
    max_retries: ${GRAPHRAG_MAX_RETRIES}
    max_retry_wait: ${GRAPHRAG_MAX_RETRY_WAIT}
    concurrent_requests: ${GRAPHRAG_CONCURRENT_REQUESTS}
    requests_per_minute: ${GRAPHRAG_CHAT_REQUESTS_PER_MINUTE}
    tokens_per_minute: ${GRAPHRAG_CHAT_TOKENS_PER_MINUTE}
  default_embedding_model:
    type: embedding
    model_provider: ${GRAPHRAG_EMBED_MODEL_PROVIDER}
    model: ${GRAPHRAG_EMBEDDING_MODEL}
    api_base: ${GRAPHRAG_EMBED_API_BASE}
    api_key: ${GRAPHRAG_EMBED_API_KEY}
    encoding_model: cl100k_base
    max_tokens: 8191
    request_timeout: ${GRAPHRAG_REQUEST_TIMEOUT}
    max_retries: ${GRAPHRAG_MAX_RETRIES}
    max_retry_wait: ${GRAPHRAG_MAX_RETRY_WAIT}
    concurrent_requests: ${GRAPHRAG_CONCURRENT_REQUESTS}
    requests_per_minute: ${GRAPHRAG_EMBED_REQUESTS_PER_MINUTE}
    tokens_per_minute: ${GRAPHRAG_EMBED_TOKENS_PER_MINUTE}

chunks:
  size: ${GRAPHRAG_CHUNK_SIZE}
  overlap: ${GRAPHRAG_CHUNK_OVERLAP}
  group_by_columns: [id]

input:
  type: file
  file_type: text
  base_dir: "input"
  file_encoding: utf-8
  file_pattern: ".*\\\\.txt$$"

cache:
  type: file
  base_dir: "cache"

storage:
  type: file
  base_dir: "output"

reporting:
  type: file
  base_dir: "output"

entity_extraction:
  entity_types: [person, organization, geo, event, concept, artifact, work, technology]
  max_gleanings: 2

summarize_descriptions:
  max_length: 500

claim_extraction:
  enabled: ${GRAPHRAG_CLAIM_EXTRACTION_ENABLED}
  max_gleanings: 1

community_reports:
  max_length: 2000
  max_input_length: 12000

embed_text:
  batch_size: ${GRAPHRAG_EMBED_BATCH_SIZE}
  batch_max_tokens: ${GRAPHRAG_EMBED_BATCH_MAX_TOKENS}

cluster_graph:
  max_cluster_size: 20

embed_graph:
  enabled: true
  num_walks: 10
  walk_length: 40
  window_size: 2
  iterations: 3
  random_seed: 42

umap:
  enabled: true

snapshots:
  graphml: false
  raw_entities: false
  top_level_nodes: false
"""


def create_graphrag_workspace() -> None:
    """Create GraphRAG workspace directories and configuration file."""
    graphrag_root = Path(settings.graphrag_root)

    # Create directories
    directories = [
        graphrag_root,
        graphrag_root / "input",
        graphrag_root / "output",
        graphrag_root / "cache",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

    # Create settings.yaml with environment variable substitution
    settings_file = graphrag_root / "settings.yaml"

    # Prepare environment variables for GraphRAG based on index provider
    index_chat_provider = settings.get_index_chat_provider()
    index_embed_provider = settings.get_index_embed_provider()
    logger.info(
        "Configuring GraphRAG for index chat provider %s and embedding provider %s",
        index_chat_provider,
        index_embed_provider,
    )

    os.environ["GRAPHRAG_CHUNK_SIZE"] = str(settings.graphrag_chunk_size)
    os.environ["GRAPHRAG_CHUNK_OVERLAP"] = str(settings.graphrag_chunk_overlap)
    os.environ["GRAPHRAG_REQUEST_TIMEOUT"] = str(settings.graphrag_request_timeout)
    os.environ["GRAPHRAG_CLAIM_EXTRACTION_ENABLED"] = str(
        settings.graphrag_claim_extraction_enabled
    ).lower()

    os.environ["GRAPHRAG_CONCURRENT_REQUESTS"] = str(settings.graphrag_concurrent_requests)
    os.environ["GRAPHRAG_MAX_RETRIES"] = str(settings.graphrag_max_retries)
    os.environ["GRAPHRAG_MAX_RETRY_WAIT"] = str(settings.graphrag_max_retry_wait)

    def provider_env(provider: str, kind: str) -> dict[str, str]:
        if provider == "ollama":
            return {
                "api_key": "ollama",
                "model": settings.ollama_llm_model
                if kind == "chat"
                else settings.ollama_embed_model,
                "api_base": settings.ollama_base_url or "",
            }
        if provider == "gemini":
            return {
                "api_key": settings.gemini_api_key or "",
                "model": settings.gemini_llm_model
                if kind == "chat"
                else settings.gemini_embed_model,
                "api_base": "",
            }
        return {
            "api_key": settings.openrouter_api_key or "",
            "model": settings.openrouter_llm_model
            if kind == "chat"
            else settings.openrouter_embed_model,
            "api_base": settings.openrouter_api_base,
        }

    chat_config = provider_env(index_chat_provider, "chat")
    embed_config = provider_env(index_embed_provider, "embedding")
    if (
        index_chat_provider == "gemini"
        and settings.gemini_free_tier_index_guard_enabled
    ):
        chat_requests_per_minute = settings.gemini_free_tier_index_rpm
        chat_tokens_per_minute = settings.gemini_free_tier_index_tpm
    else:
        chat_requests_per_minute = 1000
        chat_tokens_per_minute = 10_000_000

    if (
        index_embed_provider == "gemini"
        and settings.gemini_free_tier_embed_guard_enabled
    ):
        embed_batch_size = max(1, settings.gemini_free_tier_embed_batch_size)
        embed_requests_per_minute = max(
            1,
            int((settings.gemini_free_tier_embed_rpm * 0.8) // embed_batch_size),
        )
        embed_tokens_per_minute = settings.gemini_free_tier_embed_tpm
    else:
        embed_requests_per_minute = 1000
        embed_tokens_per_minute = 10_000_000

    os.environ["GRAPHRAG_CHAT_REQUESTS_PER_MINUTE"] = str(chat_requests_per_minute)
    os.environ["GRAPHRAG_CHAT_TOKENS_PER_MINUTE"] = str(chat_tokens_per_minute)
    os.environ["GRAPHRAG_EMBED_REQUESTS_PER_MINUTE"] = str(embed_requests_per_minute)
    os.environ["GRAPHRAG_EMBED_TOKENS_PER_MINUTE"] = str(embed_tokens_per_minute)
    os.environ["GRAPHRAG_EMBED_BATCH_SIZE"] = str(settings.gemini_free_tier_embed_batch_size)
    os.environ["GRAPHRAG_EMBED_BATCH_MAX_TOKENS"] = str(
        settings.gemini_free_tier_embed_batch_max_tokens
    )
    os.environ["GRAPHRAG_CHAT_MODEL_PROVIDER"] = index_chat_provider
    os.environ["GRAPHRAG_CHAT_MODEL"] = chat_config["model"]
    os.environ["GRAPHRAG_CHAT_TEMPERATURE"] = str(
        chat_temperature_for_model(index_chat_provider, chat_config["model"])
    )
    os.environ["GRAPHRAG_CHAT_API_BASE"] = chat_config["api_base"]
    os.environ["GRAPHRAG_CHAT_API_KEY"] = chat_config["api_key"]
    os.environ["GRAPHRAG_EMBED_MODEL_PROVIDER"] = index_embed_provider
    os.environ["GRAPHRAG_EMBEDDING_MODEL"] = embed_config["model"]
    os.environ["GRAPHRAG_EMBED_API_BASE"] = embed_config["api_base"]
    os.environ["GRAPHRAG_EMBED_API_KEY"] = embed_config["api_key"]

    settings_file.write_text(SETTINGS_YAML_CONTENT)
    logger.info(f"Created GraphRAG configuration: {settings_file}")

    logger.info("GraphRAG workspace initialized successfully!")
    logger.info(f"Place your text documents in: {graphrag_root / 'input'}")


def main() -> None:
    """Main initialization logic."""
    logger.info("Starting GraphRAG workspace initialization...")

    try:
        create_graphrag_workspace()
    except Exception as e:
        logger.error(f"GraphRAG initialization failed: {e}")
        raise


if __name__ == "__main__":
    main()
