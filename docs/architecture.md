# Architecture

## 当前版本

当前版本是 2-step RAG：

1. 文档入库：Upload -> LangChain Loader -> Text Splitter -> Embeddings -> Local JSON Vector Store。
2. 问答：Question -> Retriever -> Prompt -> LLM -> Answer + Sources。

## 边界

- API 层只处理 HTTP request/response。
- RAG chain 只负责编排，不直接读取环境变量。
- Retriever 是后续 agent 化的关键边界：现在由 chain 调用，后续可以包装成 tool。
- LLM、Embedding、VectorStore 都通过 factory 创建，避免业务代码绑定具体供应商。

## 后续迁移

旧项目里的 Azure AI Search、权限过滤、rerank 可以逐步迁移到：

- `rag/vectorstores/azure_search_store.py`
- `rag/retrievers/acl_retriever.py`
- `rag/retrievers/rerank_retriever.py`
