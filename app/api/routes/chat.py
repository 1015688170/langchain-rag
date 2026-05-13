from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.dependencies import get_rag_chain
from app.domain.schemas import ChatRequest, ChatResponse
from app.rag.chains.rag_chain import RagChain


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, rag_chain: RagChain = Depends(get_rag_chain)) -> ChatResponse:
    return rag_chain.answer(request.question, request.top_k)

