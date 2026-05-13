from __future__ import annotations

import json
import math
import uuid
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


class LocalJsonVectorStore:
    """Small local vector store for development and smoke tests."""

    def __init__(self, filepath: Path, embeddings: Embeddings) -> None:
        self.filepath = filepath
        self.embeddings = embeddings
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def add_documents(self, documents: list[Document]) -> list[str]:
        records = self._load_records()
        texts = [document.page_content for document in documents]
        vectors = self.embeddings.embed_documents(texts)
        ids: list[str] = []
        for document, vector in zip(documents, vectors, strict=True):
            record_id = str(document.metadata.get("source_id") or uuid.uuid4().hex)
            ids.append(record_id)
            records.append(
                {
                    "id": record_id,
                    "content": document.page_content,
                    "metadata": self._json_safe_metadata(document.metadata),
                    "vector": vector,
                }
            )
        self._save_records(records)
        return ids

    def similarity_search_with_scores(self, query: str, top_k: int) -> list[tuple[Document, float]]:
        records = self._load_records()
        if not records:
            return []

        query_vector = self.embeddings.embed_query(query)
        scored = [
            (record, self._cosine_similarity(query_vector, record["vector"]))
            for record in records
        ]
        scored.sort(key=lambda item: item[1], reverse=True)
        results: list[tuple[Document, float]] = []
        for record, score in scored[:top_k]:
            results.append(
                (
                    Document(
                        page_content=str(record["content"]),
                        metadata=dict(record.get("metadata") or {}) | {"id": record["id"]},
                    ),
                    score,
                )
            )
        return results

    def _load_records(self) -> list[dict[str, Any]]:
        if not self.filepath.exists():
            return []
        return json.loads(self.filepath.read_text(encoding="utf-8"))

    def _save_records(self, records: list[dict[str, Any]]) -> None:
        self.filepath.write_text(
            json.dumps(records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _cosine_similarity(self, left: list[float], right: list[float]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        dot = sum(a * b for a, b in zip(left, right, strict=True))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return dot / (left_norm * right_norm)

    def _json_safe_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        safe: dict[str, Any] = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                safe[key] = value
            else:
                safe[key] = str(value)
        return safe
