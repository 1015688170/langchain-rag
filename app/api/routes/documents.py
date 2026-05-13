from __future__ import annotations

import re
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.config import Settings
from app.core.dependencies import get_vector_store, settings_dependency
from app.domain.schemas import IngestResponse
from app.rag.loaders.file_loader import load_and_split_file
from app.rag.vectorstores.local_json_store import LocalJsonVectorStore


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    settings: Settings = Depends(settings_dependency),
    store: LocalJsonVectorStore = Depends(get_vector_store),
) -> IngestResponse:
    filename = _safe_filename(file.filename or "")
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    document_id = uuid.uuid4().hex
    document_dir = settings.upload_dir / document_id
    document_dir.mkdir(parents=True, exist_ok=True)
    filepath = document_dir / filename
    await _save_upload(file, filepath)

    try:
        chunks = load_and_split_file(filepath, settings.chunk_size, settings.chunk_overlap)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not chunks:
        raise HTTPException(status_code=400, detail="Uploaded file has no extractable text.")
    for chunk in chunks:
        chunk.metadata["document_id"] = document_id
        chunk.metadata["source_id"] = f"{document_id}:{chunk.metadata['chunk_index']}"

    vector_ids = store.add_documents(chunks)
    return IngestResponse(
        document_id=document_id,
        filename=filename,
        chunk_count=len(chunks),
        vector_ids=vector_ids,
    )


async def _save_upload(file: UploadFile, filepath: Path) -> None:
    with filepath.open("wb") as output:
        while chunk := await file.read(1024 * 1024):
            output.write(chunk)


def _safe_filename(filename: str) -> str:
    name = Path(filename).name.strip().replace("\\", "_").replace("/", "_")
    return re.sub(r"[^A-Za-z0-9._ -]", "_", name)
