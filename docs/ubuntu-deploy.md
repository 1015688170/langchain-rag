# Ubuntu 部署说明

默认部署整个仓库到 `/opt/swp-rag-workbench/current`，新项目目录为 `/opt/swp-rag-workbench/current/langchain-rag`，服务端口为 `8010`。

## 1. 安装系统依赖

Ubuntu 24.04 默认 Python 3.12，可直接使用；Ubuntu 22.04 默认 Python 3.10，不满足本项目 `>=3.11,<3.13`，建议先安装 Python 3.11 或 3.12。

```bash
sudo apt update
sudo apt install -y git curl nginx
sudo apt install -y python3 python3-venv python3-pip
python3 --version
```

如果 `python3 --version` 小于 3.11，先换成 Python 3.11/3.12 后再继续。

## 2. 拉取代码

```bash
sudo mkdir -p /opt/swp-rag-workbench/current
sudo chown -R "$USER:$USER" /opt/swp-rag-workbench

git clone <你的仓库地址> /opt/swp-rag-workbench/current
cd /opt/swp-rag-workbench/current/langchain-rag
```

如果已经上传了代码，只需要进入目录：

```bash
cd /opt/swp-rag-workbench/current/langchain-rag
```

## 3. 创建虚拟环境

```bash
python3 -m venv /opt/swp-rag-workbench/venv-langchain-rag
source /opt/swp-rag-workbench/venv-langchain-rag/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -e .
```

## 4. 创建环境变量

本地烟测可以先用默认的 `echo` 和 `hash`：

```bash
cp .env.example .env
mkdir -p data/uploads
```

服务器已有密钥文件时，不要把密钥复制进代码仓库；让进程读取系统环境变量即可。当前约定文件：

```bash
sudo test -r /opt/swp-rag-workbench/env/backend.env
sudo -u "$USER" test -r /opt/swp-rag-workbench/env/backend.env
test -d /opt/swp-models/bge-reranker-v2-m3
```

`backend.env` 给 systemd 使用时应保持 `KEY=VALUE` 格式，不要依赖 shell 专属写法。

手动前台验证真实模型时，先加载密钥文件：

```bash
set -a
. /opt/swp-rag-workbench/env/backend.env
set +a
```

真实模型配置示例：

```env
LLM_PROVIDER=nexus
EMBEDDING_PROVIDER=nexus
NEXUS_API_KEY=xxx
NEXUS_CHAT_API_URL=https://xxx
NEXUS_EMBEDDING_API_URL=https://xxx
NEXUS_CHAT_MODEL=gpt-4o
VECTORSTORE_PATH=./data/vectorstore.json
UPLOAD_DIR=./data/uploads
```

## 5. 手动启动验证

```bash
cd /opt/swp-rag-workbench/current/langchain-rag
source /opt/swp-rag-workbench/venv-langchain-rag/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8010
```

另开一个终端验证：

```bash
curl http://127.0.0.1:8010/api/health
curl -F "file=@README.md" http://127.0.0.1:8010/api/documents
curl -X POST http://127.0.0.1:8010/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"这个项目是什么？","top_k":3}'
```

验证完成后，在启动终端按 `Ctrl+C` 停止。

## 6. 配置 systemd

把 `User=ubuntu` 改成实际运行用户。

```bash
sudo tee /etc/systemd/system/langchain-rag.service > /dev/null <<'EOF'
[Unit]
Description=LangChain RAG FastAPI Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/swp-rag-workbench/current/langchain-rag
EnvironmentFile=/opt/swp-rag-workbench/env/backend.env
Environment=RERANKER_MODEL_PATH=/opt/swp-models/bge-reranker-v2-m3
ExecStart=/opt/swp-rag-workbench/venv-langchain-rag/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

如果当前用户不是 `ubuntu`：

```bash
sudo sed -i "s/^User=.*/User=$USER/" /etc/systemd/system/langchain-rag.service
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable langchain-rag
sudo systemctl start langchain-rag
sudo systemctl status langchain-rag
```

查看日志：

```bash
journalctl -u langchain-rag -f
```

## 7. 配置 Nginx

```bash
sudo tee /etc/nginx/sites-available/langchain-rag > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;
    client_max_body_size 25m;

    location /api/ {
        proxy_pass http://127.0.0.1:8010/api/;
        proxy_http_version 1.1;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/langchain-rag /etc/nginx/sites-enabled/langchain-rag
sudo nginx -t
sudo systemctl reload nginx
```

验证 Nginx：

```bash
curl http://127.0.0.1/api/health
```

## 8. 日常更新

```bash
cd /opt/swp-rag-workbench/current
git pull
cd langchain-rag
source /opt/swp-rag-workbench/venv-langchain-rag/bin/activate
pip install -e .
sudo systemctl restart langchain-rag
journalctl -u langchain-rag -n 100 --no-pager
```

## 9. 常见排查

端口是否监听：

```bash
ss -lntp | grep 8010
```

服务状态：

```bash
sudo systemctl status langchain-rag
```

直接跑前台看错误：

```bash
cd /opt/swp-rag-workbench/current/langchain-rag
source /opt/swp-rag-workbench/venv-langchain-rag/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8010
```

清空本地烟测向量数据：

```bash
cd /opt/swp-rag-workbench/current/langchain-rag
rm -f data/vectorstore.json
```
