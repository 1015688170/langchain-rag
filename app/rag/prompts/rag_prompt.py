from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate


RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "你是企业内部知识库的 RAG 问答助手。"
                "必须严格依据参考资料回答；如果资料不足，直接说明当前资料没有足够依据。"
                "不要编造来源，不要使用参考资料之外的信息。"
            ),
        ),
        (
            "human",
            "【参考资料】\n{context}\n\n【问题】\n{question}",
        ),
    ]
)

