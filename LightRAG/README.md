# LightRAG API-only 部署指南

本指南说明如何在 Pisces 项目中，以“仅 API”方式部署 LightRAG 服务，并让 `api` 端通过 HTTP 接口消费图谱能力。文档默认你在仓库根目录下创建了 `LightRAG/` 目录。

## 1. 目录结构约定

```
LightRAG/
├── lightrag/              # 上游 LightRAG 源码（git clone 的结果）
├── data/
│   ├── rag_storage/       # 持久化图谱/向量索引
│   └── inputs/            # Pisces 上传的事件/告警临时输入
├── Dockerfile.api         # API-only 构建文件（见官方示例，可按需自定义）
├── env.example            # 环境变量示例（上游提供）
├── .env                   # LLM / 向量模型等敏感配置
└── README.md              # 本文件
```

> 目录中必须包含 `LightRAG/lightrag`。推荐在 Pisces 根目录执行：
> ```powershell
> cd C:\Users\Administrator\Desktop\pisces
> git clone https://github.com/HKUDS/LightRAG.git LightRAG\lightrag
> ```
> 如果 `LightRAG/lightrag` 已存在，可进入该目录后 `git pull origin main` 保持最新。

## 2. 前置要求

- Docker 24+ 与 Docker Compose v2
- Python 3.10+（本地调试或构建镜像时使用）
- 可用的 LLM API Key（OpenAI、Azure OpenAI、Google 等任一提供商）
- 可选：向量存储依赖（本地 FAISS、Milvus、PGVector…），与 LightRAG 官方配置保持一致

## 3. 配置文件

### 3.1 `.env`

LightRAG 提供 `env.example` 作为参考。在 `LightRAG/` 目录执行：

```powershell
cd LightRAG
Copy-Item env.example .env
# 或 Linux/macOS: cp env.example .env
```

然后编辑 `.env`，填入模型凭据与向量索引配置，关键字段包括：

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-large
VECTOR_DB=faiss
VECTOR_STORE_PATH=/app/data/rag_storage
```

根据所选云厂商替换为 Azure (`AZURE_OPENAI_ENDPOINT` / `AZURE_OPENAI_KEY`) 或其它兼容变量。

### 3.2 数据目录

初始化持久化目录：

```powershell
mkdir -Force LightRAG\data\rag_storage
mkdir -Force LightRAG\data\inputs
```

这两个路径会通过 Volume 挂载到容器内 `/app/data/*`，避免容器重启导致图谱丢失。

### 3.4 绕过 WebUI 构建

LightRAG 默认会尝试构建自带的前端 WebUI。为了实现「纯 API」部署，可在源码目录下放置一个空白 `index.html`，这样构建流程会直接复用该文件而无需安装前端依赖：

```powershell
$webui = "LightRAG\lightrag\api\webui"
mkdir -Force $webui | Out-Null
Set-Content -Path "$webui\index.html" -Value "" -Encoding utf8
```

> 若你使用 Linux/macOS，可改为 `mkdir -p LightRAG/lightrag/api/webui && touch LightRAG/lightrag/api/webui/index.html`。

执行完毕后，无需安装 Node.js/Web 前端依赖即可构建 API-only 镜像。

> 如果仓库中自带 `Dockerfile.api.example` / `env.example`，建议在上述步骤前执行：
> ```powershell
> Copy-Item Dockerfile.api.example Dockerfile.api
> Copy-Item env.example .env
> ```
> Linux/macOS 使用 `cp` 命令即可。

## 4. 构建 API-only 镜像

1. 切换到 `LightRAG/`：
   ```powershell
   cd LightRAG
   ```
2. 如果 upstream 提供 `Dockerfile.api.example`，复制后再按需修改：
   ```powershell
   Copy-Item Dockerfile.api.example Dockerfile.api
   ```
   如需自定义，可在复制后的 `Dockerfile.api` 中调整基础镜像或依赖。
3. 构建镜像：
   ```powershell
   docker build -f Dockerfile.api -t lightrag:latest .
   ```

> 如果启用了 GPU，可在 Dockerfile 中切换至 `nvidia/cuda` 基础镜像并在 `docker run` / compose 中声明 `runtime: nvidia`。

## 5. 运行 LightRAG API

### 5.1 单独运行

```powershell
docker run -d --name lightrag `
  -p 9621:9621 `
  --env-file ./LightRAG/.env `
  -v ${PWD}/LightRAG/data/rag_storage:/app/data/rag_storage `
  -v ${PWD}/LightRAG/data/inputs:/app/data/inputs `
  lightrag:latest
```

### 5.2 与 Pisces Compose 集成

在根目录的 `docker-compose.yaml` 中加入（或启用）以下服务：

```
  lightrag:
    container_name: lightrag
    image: lightrag:latest
    build:
      context: ./LightRAG
      dockerfile: Dockerfile.api
    ports:
      - "9621:9621"
    volumes:
      - ./LightRAG/lightrag:/app/lightrag:delegated
      - ./LightRAG/data/rag_storage:/app/data/rag_storage
      - ./LightRAG/data/inputs:/app/data/inputs
      - ./LightRAG/.env:/app/.env
    env_file:
      - ./LightRAG/.env
    restart: always
```

执行 `docker compose up -d lightrag` 即可启动 API 服务。

## 6. 健康检查与验收

1. 健康检查：
   ```bash
   curl http://localhost:9621/health
   ```
   返回 `{"status":"ok"}` 或类似内容即表示 API 正常。

2. 上传测试文档：
   ```bash
   curl -X POST http://localhost:9621/documents/text \
     -H "Content-Type: application/json" \
     -d '{"text": "Pisces incident example"}'
   ```
3. 查询图谱：
   ```bash
   curl "http://localhost:9621/graphs?label=*&max_depth=2"
   ```

## 7. Pisces 侧配置

在 `api/resources/config.yaml` 中设置：

```
application:
  lightrag:
    base_url: "http://lightrag:9621"
    api_key: ""              # 如 LightRAG 启用 API Key，在此填入
    request_timeout_seconds: 60
    poll_interval_seconds: 3
```

随后重启 `pisces_api` 服务，使后端能够调用 LightRAG 生成事件图谱与摘要。

## 8. 构建 & 启动流程速览（docker compose）

在 Pisces 根目录按顺序执行：

```powershell
docker compose build lightrag
docker compose up -d lightrag
```

若要一次性启动所有服务，可执行 `docker compose up -d`。

## 9. 常见问题排查

- **无法连接模型提供商**：确认 `.env` 中的 `OPENAI_API_KEY`、`AZURE_*` 或自定义变量拼写正确，并测试 `curl`/`python` 是否可访问。
- **向量索引未持久化**：确保 `./data/rag_storage` 已挂载到容器内 `/app/data/rag_storage`，并具有写权限。
- **Pisces 报告 “LightRAG base_url 未配置”**：检查 `config.yaml`，并确认 `pisces_api` 已重新加载配置。
- **Graph 构建超时**：调高 `workspace_timeout_seconds` / `track_timeout_seconds`，或增大容器资源（CPU、RAM、网络）。

如需更高级的 RAG 管理（多 workspace、多 collection、GPU 加速），请参考上游 LightRAG 官方文档并同步更新本 README。


