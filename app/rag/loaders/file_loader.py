from __future__ import annotations

import re
from pathlib import Path

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


SUPPORTED_EXTENSIONS = {".md", ".txt", ".json", ".pdf", ".docx"}


def load_and_split_file(filepath: Path, chunk_size: int, chunk_overlap: int) -> list[Document]:
    suffix = filepath.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported file type: {suffix}. Supported: {supported}.")

    documents = _load_file(filepath, suffix)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "；", ";", ".", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    for index, chunk in enumerate(chunks):
        chunk.page_content = _normalize_text(chunk.page_content)
        chunk.metadata["chunk_index"] = index
        chunk.metadata["filename"] = filepath.name
        chunk.metadata["filepath"] = str(filepath)
        chunk.metadata["source_type"] = suffix.lstrip(".")
    return [chunk for chunk in chunks if chunk.page_content.strip()]


def _load_file(filepath: Path, suffix: str) -> list[Document]:
    if suffix in {".md", ".txt", ".json"}:
        return TextLoader(str(filepath), encoding="utf-8").load()
    if suffix == ".pdf":
        return PyPDFLoader(str(filepath)).load()
    if suffix == ".docx":
        return Docx2txtLoader(str(filepath)).load()
    raise ValueError(f"Unsupported file type: {suffix}.")


def _normalize_text(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text).strip()

