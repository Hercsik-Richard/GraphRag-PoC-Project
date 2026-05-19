"""Initialize GraphRAG workspace directories and configuration."""

import logging
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import settings  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SETTINGS_YAML_CONTENT = """# GraphRAG Configuration for Mythology Project

encoding_model: cl100k_base

models:
  default_chat_model:
    type: chat
    model_provider: ${GRAPHRAG_MODEL_PROVIDER}
    model: ${GRAPHRAG_LLM_MODEL}
    api_base: ${GRAPHRAG_API_BASE}
    api_key: ${GRAPHRAG_API_KEY}
    encoding_model: cl100k_base
    max_tokens: 4000
    temperature: 0
    top_p: 1
    request_timeout: ${GRAPHRAG_REQUEST_TIMEOUT}
    max_retries: ${GRAPHRAG_MAX_RETRIES}
    max_retry_wait: ${GRAPHRAG_MAX_RETRY_WAIT}
    concurrent_requests: ${GRAPHRAG_CONCURRENT_REQUESTS}
  default_embedding_model:
    type: embedding
    model_provider: ${GRAPHRAG_MODEL_PROVIDER}
    model: ${GRAPHRAG_EMBEDDING_MODEL}
    api_base: ${GRAPHRAG_API_BASE}
    api_key: ${GRAPHRAG_API_KEY}
    encoding_model: cl100k_base
    max_tokens: 8191
    request_timeout: ${GRAPHRAG_REQUEST_TIMEOUT}
    max_retries: ${GRAPHRAG_MAX_RETRIES}
    max_retry_wait: ${GRAPHRAG_MAX_RETRY_WAIT}
    concurrent_requests: ${GRAPHRAG_CONCURRENT_REQUESTS}

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
  entity_types: [person, place, event, concept, artifact]
  max_gleanings: 1

summarize_descriptions:
  max_length: 500

claim_extraction:
  enabled: ${GRAPHRAG_CLAIM_EXTRACTION_ENABLED}
  max_gleanings: 1

community_reports:
  max_length: 1500
  max_input_length: 8000

cluster_graph:
  max_cluster_size: 10

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
    index_provider = settings.get_index_provider()
    logger.info(f"Configuring GraphRAG for index provider: {index_provider}")

    os.environ["GRAPHRAG_CHUNK_SIZE"] = str(settings.graphrag_chunk_size)
    os.environ["GRAPHRAG_CHUNK_OVERLAP"] = str(settings.graphrag_chunk_overlap)
    os.environ["GRAPHRAG_REQUEST_TIMEOUT"] = str(settings.graphrag_request_timeout)
    os.environ["GRAPHRAG_CLAIM_EXTRACTION_ENABLED"] = str(
        settings.graphrag_claim_extraction_enabled
    ).lower()

    if index_provider == "ollama":
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
    elif index_provider == "gemini":
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
