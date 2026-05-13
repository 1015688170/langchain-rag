# Agent Roadmap

## 阶段 1：稳定 RAG

- 固定执行检索。
- 固定执行一次生成。
- 控制延迟和答案边界。

## 阶段 2：Retriever Tool

- 把 `LangChainRetriever.retrieve()` 包装成 tool。
- tool 输入先只保留 `query` 和 `top_k`。
- 保留来源 metadata，便于 agent 输出引用。

## 阶段 3：Agentic RAG

- LLM 决定是否检索。
- 支持多次检索、问题改写、结果校验。
- 引入 LangGraph 管理状态：`query -> decide -> retrieve -> grade -> generate`。

