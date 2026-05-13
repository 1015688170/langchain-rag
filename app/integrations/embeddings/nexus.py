from __future__ import annotations

import requests
from langchain_core.embeddings import Embeddings


class NexusEmbeddings(Embeddings):
    def __init__(self, api_url: str, api_key: str, timeout: int = 30) -> None:
        if not api_url:
            raise ValueError("NEXUS_EMBEDDING_API_URL must be set when EMBEDDING_PROVIDER=nexus.")
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        response = requests.post(
            self.api_url,
            headers={"Content-Type": "application/json", "api-key": self.api_key},
            json={"input": text, "user": "langchain-rag"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]

