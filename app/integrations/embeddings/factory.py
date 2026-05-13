from __future__ import annotations

from langchain_core.embeddings import Embeddings

from app.core.config import Settings
from app.integrations.embeddings.hash import HashEmbeddings
from app.integrations.embeddings.nexus import NexusEmbeddings


def create_embeddings(settings: Settings) -> Embeddings:
    if settings.embedding_provider == "hash":
        return HashEmbeddings()

    if settings.embedding_provider == "nexus":
        return NexusEmbeddings(
            api_url=settings.nexus_embedding_api_url,
            api_key=settings.nexus_api_key,
        )

    if settings.embedding_provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url or None,
        )

    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")

