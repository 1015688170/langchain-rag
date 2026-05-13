from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


LlmProviderName = Literal["echo", "nexus", "openai"]
EmbeddingProviderName = Literal["hash", "nexus", "openai"]
RerankerProviderName = Literal["none", "local"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "LangChain RAG API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    cors_allow_origins: list[str] = Field(default_factory=lambda: ["*"])

    llm_provider: LlmProviderName = "echo"
    embedding_provider: EmbeddingProviderName = "hash"

    nexus_api_key: str = ""
    nexus_chat_api_url: str = ""
    nexus_embedding_api_url: str = ""
    nexus_chat_model: str = "gpt-4o"

    openai_api_key: str = ""
    openai_base_url: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    vectorstore_path: Path = Path("./data/vectorstore.json")
    upload_dir: Path = Path("./data/uploads")

    chunk_size: int = 1000
    chunk_overlap: int = 150
    top_k: int = 5
    min_relevance_score: float = 0.0

    reranker_provider: RerankerProviderName = "none"
    reranker_model_path: Path = Path("/opt/swp-models/bge-reranker-v2-m3")
    reranker_top_n: int = 5

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def parse_cors_allow_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if not value:
            return ["*"]
        if value.strip().startswith("["):
            return [str(item) for item in json.loads(value)]
        return [item.strip() for item in value.split(",") if item.strip()]

    def ensure_directories(self) -> None:
        self.vectorstore_path.parent.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
