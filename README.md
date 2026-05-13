# LangChain RAG

一个干净的新项目骨架：先实现 LangChain + 2-step RAG，后续可以把 retriever 包装成 tool，升级为 LangChain Agent 或 LangGraph。

## 结构

```text
app/
  api/routes/              # HTTP 接口
  core/                    # 配置、依赖装配
  domain/                  # 请求/响应模型
  integrations/            # LLM、Embedding 适配器
  rag/
    chains/                # RAG 编排
    loaders/               # 文件加载和切块
    prompts/               # Prompt
    retrievers/            # 检索边界，后续可转 tool
    vectorstores/          # 本地 JSON / Azure AI Search 等向量库适配
```

## 本地启动

```powershell
cd langchain-rag
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

默认 `LLM_PROVIDER=echo`、`EMBEDDING_PROVIDER=hash`，本地向量库为 JSON 文件，只用于接口烟测；真实效果需要切到 Nexus 或 OpenAI 兼容模型，并把向量库替换为 Azure AI Search 等生产组件。

Ubuntu 部署命令见 [docs/ubuntu-deploy.md](docs/ubuntu-deploy.md)。

## API

```bash
curl http://127.0.0.1:8000/api/health
```

```bash
curl -F "file=@README.md" http://127.0.0.1:8000/api/documents
```

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"这个项目是什么？","top_k":3}'
```

## 生产配置

Nexus：

```env
LLM_PROVIDER=nexus
EMBEDDING_PROVIDER=nexus
NEXUS_API_KEY=xxx
NEXUS_CHAT_API_URL=https://...
NEXUS_EMBEDDING_API_URL=https://...
```

OpenAI 兼容接口：

```env
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=xxx
OPENAI_BASE_URL=https://...
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```
