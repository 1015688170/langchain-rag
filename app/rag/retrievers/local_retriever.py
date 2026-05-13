from __future__ import annotations

from dataclasses import dataclass

from langchain_core.documents import Document

from app.rag.vectorstores.local_json_store import LocalJsonVectorStore


@dataclass(frozen=True)
class RetrievedDocument:
    document: Document
    score: float | None


class LangChainRetriever:
    """Agent-ready retrieval boundary."""

    def __init__(self, store: LocalJsonVectorStore, min_relevance_score: float = 0.0) -> None:
        self.store = store
        self.min_relevance_score = min_relevance_score

    def retrieve(self, query: str, top_k: int) -> list[RetrievedDocument]:
        results = self.store.similarity_search_with_scores(query, top_k)
        retrieved: list[RetrievedDocument] = []
        for document, score in results:
            if score is not None and score < self.min_relevance_score:
                continue
            retrieved.append(RetrievedDocument(document=document, score=score))
        return retrieved
