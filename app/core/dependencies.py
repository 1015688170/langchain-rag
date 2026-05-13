from __future__ import annotations

from functools import lru_cache

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import Settings, get_settings
from app.integrations.embeddings.factory import create_embeddings
from app.integrations.llms.factory import create_chat_model
from app.rag.chains.rag_chain import RagChain
from app.rag.retrievers.local_retriever import LangChainRetriever
from app.rag.vectorstores.local_json_store import LocalJsonVectorStore


@lru_cache
def get_embeddings() -> Embeddings:
    return create_embeddings(get_settings())


@lru_cache
def get_chat_model() -> BaseChatModel:
    return create_chat_model(get_settings())


@lru_cache
def get_vector_store() -> LocalJsonVectorStore:
    settings = get_settings()
    return LocalJsonVectorStore(
        filepath=settings.vectorstore_path,
        embeddings=get_embeddings(),
    )


@lru_cache
def get_retriever() -> LangChainRetriever:
    settings = get_settings()
    return LangChainRetriever(
        store=get_vector_store(),
        min_relevance_score=settings.min_relevance_score,
    )


@lru_cache
def get_rag_chain() -> RagChain:
    settings = get_settings()
    return RagChain(
        llm=get_chat_model(),
        retriever=get_retriever(),
        default_top_k=settings.top_k,
    )


def settings_dependency() -> Settings:
    return get_settings()
