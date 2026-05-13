from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser

from app.domain.schemas import ChatResponse, SourceItem
from app.rag.prompts.rag_prompt import RAG_PROMPT
from app.rag.retrievers.local_retriever import LangChainRetriever, RetrievedDocument


class RagChain:
    def __init__(self, llm: BaseChatModel, retriever: LangChainRetriever, default_top_k: int) -> None:
        self.llm = llm
        self.retriever = retriever
        self.default_top_k = default_top_k
        self.chain = RAG_PROMPT | self.llm | StrOutputParser()

    def answer(self, question: str, top_k: int | None = None) -> ChatResponse:
        retrieved = self.retriever.retrieve(question, top_k or self.default_top_k)
        if not retrieved:
            return ChatResponse(
                answer="当前知识库没有检索到足够相关的资料，无法生成有依据的回答。",
                sources=[],
                source_count=0,
            )

        answer = self.chain.invoke(
            {
                "question": question,
                "context": self._format_context(retrieved),
            }
        )
        sources = [self._to_source_item(item) for item in retrieved]
        return ChatResponse(answer=answer, sources=sources, source_count=len(sources))

    def _format_context(self, retrieved: list[RetrievedDocument]) -> str:
        blocks: list[str] = []
        for index, item in enumerate(retrieved, start=1):
            metadata = item.document.metadata
            filename = metadata.get("filename") or metadata.get("source") or "unknown"
            page = metadata.get("page")
            source = f"{filename}"
            if page is not None:
                source = f"{source}#page={int(page) + 1}"
            blocks.append(
                f"[{index}] source={source} score={item.score}\n{item.document.page_content}"
            )
        return "\n\n".join(blocks)

    def _to_source_item(self, item: RetrievedDocument) -> SourceItem:
        metadata = item.document.metadata
        content = " ".join(item.document.page_content.split())
        page = metadata.get("page")
        return SourceItem(
            source_id=str(metadata.get("source_id") or metadata.get("id") or ""),
            filename=str(metadata.get("filename") or metadata.get("source") or "unknown"),
            filepath=str(metadata.get("filepath") or metadata.get("source") or ""),
            score=item.score,
            page=int(page) + 1 if page is not None else None,
            preview=content[:220],
        )

