from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import Settings
from app.integrations.llms.echo import EchoChatModel
from app.integrations.llms.nexus import NexusChatModel


def create_chat_model(settings: Settings) -> BaseChatModel:
    if settings.llm_provider == "echo":
        return EchoChatModel()

    if settings.llm_provider == "nexus":
        return NexusChatModel(
            api_url=settings.nexus_chat_api_url,
            api_key=settings.nexus_api_key,
            model=settings.nexus_chat_model,
        )

    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.openai_chat_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url or None,
            temperature=0.2,
        )

    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

