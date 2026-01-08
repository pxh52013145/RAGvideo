# 本地 <-> Dify 知识库对账/同步（MinIO 原文真源）部署说明

## 1. 你会得到什么
- 启动/切换 Dify Profile 后自动对账：`LOCAL_ONLY`（本地有）、`DIFY_ONLY`（Dify 有）、`DIFY_ONLY_NO_BUNDLE`（远端缺包）、`SYNCED`、`PARTIAL`（部分同步）、`CONFLICT`（冲突）、`DELETED`（墓碑删除）、`DIFY_ONLY_LEGACY`
- `LOCAL_ONLY/PARTIAL` 可点“入库”：上传原文包到 MinIO + 写入/补齐当前 Dify 数据集
- `DIFY_ONLY/PARTIAL` 可点“获取/补全”：从 MinIO 拉取原文包到本地（只补缺失文件，避免重复生成本地条目）
- `CONFLICT` 可点“本地覆盖 / 云端覆盖 / 另存副本”：用 hash 判断不一致，并提供可控的覆盖/保留策略
- 可点“删本地”：删除本地任务目录与文件；可点“删远端”：写入 MinIO tombstone，并尝试删除 Dify 文档

## 2. 部署与配置（按你的运行方式）
你有两种常见方式：
- 方式 A（推荐）：本项目（前端+后端）运行在本地；服务器只提供 Dify + MinIO
- 方式 B：本项目（前端+后端）也运行在服务器（docker compose）；客户端用浏览器访问

下面步骤里：
- “服务器”主要指 **MinIO 所在机器**
- `MINIO_*` 这组配置要写在 **后端运行的环境**（本地跑后端就写本地；服务器跑后端就写服务器）

### 2.1 部署 MinIO（推荐 Docker）
在 **MinIO 所在服务器** 上执行（示例：数据落盘到 `/srv/minio`，对外端口用 9000/9001）：

```bash
mkdir -p /srv/minio
docker run -d --name minio \
  --restart unless-stopped \
  -p 9000:9000 -p 9001:9001 \
  -v /srv/minio:/data \
  -e MINIO_ROOT_USER="ragvideo" \
  -e MINIO_ROOT_PASSWORD="CHANGE_ME_STRONG_PASSWORD" \
  quay.io/minio/minio server /data --console-address ":9001"
```

说明：
- 9000：S3 API；9001：MinIO Console
- 如果 9000/9001 已被占用（例如你的 Dify 用了 9000），只需要改映射端口即可，例如：

```bash
docker run -d --name minio \
  --restart unless-stopped \
  -p 9100:9000 -p 9101:9001 \
  -v /srv/minio:/data \
  -e MINIO_ROOT_USER="ragvideo" \
  -e MINIO_ROOT_PASSWORD="CHANGE_ME_STRONG_PASSWORD" \
  quay.io/minio/minio server /data --console-address ":9001"
```
- 改端口后，记得同步修改后端的 `MINIO_ENDPOINT`：
  - 后端在同一台服务器：例如 `127.0.0.1:9100`
  - 后端在你本地电脑：例如 `<服务器IP>:9100`
- 若你要走 HTTPS/域名反代，请保证后端访问的 `MINIO_ENDPOINT` 与证书一致，并把 `MINIO_SECURE=true`

### 2.2 配置后端环境变量（.env）
把以下变量写入 **后端运行环境** 的 `.env`（或 systemd/docker env）：

```env
# MinIO endpoint 不要带 http/https 前缀，只写 host:port
# - 方式 A（本地跑后端，MinIO 在服务器）：MINIO_ENDPOINT=<服务器IP>:9100
# - 方式 B（后端也在服务器宿主机）：MINIO_ENDPOINT=127.0.0.1:9100
# - 如果后端跑在 Docker：不要用 127.0.0.1（那是容器自身），请用可路由地址（例如 minio:9000 或服务器 IP:9100）
MINIO_ENDPOINT=
MINIO_ACCESS_KEY=ragvideo
MINIO_SECRET_KEY=CHANGE_ME_STRONG_PASSWORD
MINIO_SECURE=false

# 按 Dify Profile 隔离 bucket：bucket 由 profile 名称派生（S3 安全 slug + hash）+ 前缀
MINIO_BUCKET_PREFIX=ragvideo-
MINIO_OBJECT_PREFIX=bundles/
MINIO_TOMBSTONE_PREFIX=tombstones/
MINIO_REGION=
```

Bucket 规则：
- 后端会按当前 active_profile 自动计算 bucket（S3 仅允许 `a-z0-9.-`），并追加 8 位 hash 避免不同 profile 撞名（例如中文 profile）。
- 例如：active_profile=`default` → bucket 类似 `ragvideo-default-<hash8>`
- 例如：active_profile=`server-prod` → bucket 类似 `ragvideo-server-prod-<hash8>`
- 后端会自动 `ensure_bucket`，前提是该 MinIO 账号有创建 bucket 的权限（Root 用户默认有）。

### 2.3 更新后端依赖并重启服务
你需要确保后端安装了 `minio` 依赖（已加入 `backend/requirements.txt`）。

#### 情况 A：你用 docker-compose 跑后端
```bash
docker compose up -d --build backend
```
如果你也需要更新前端（知识库页新增“对账/入库/获取”按钮），建议：
```bash
docker compose up -d --build
```

#### 情况 B：你直接在宿主机运行 Python
```bash
pip install -r backend/requirements.txt
python backend/main.py
```

### 2.4 配置 Dify（每个 Profile）
在前端设置页 `设置 → Dify` 为每个 Profile 填：
- `base_url`
- `dataset_id`（以及可选的 `note_dataset_id` / `transcript_dataset_id`）
- `service_api_key`（写入知识库必须）
- 保存后会触发一次同步扫描

## 3. 验证方式

### 3.1 用接口验证
```bash
curl -X POST http://<backend-host>:8483/api/sync/scan
```
能看到 `items[]` 且 `minio_bucket` 非空即表示 MinIO 配置生效（扫描需要 Dify key 才能读远端列表）。

扫描结果会同时落库到 SQLite（表：`sync_items`，按 `profile` 维度分区），便于前端快速渲染与排错。

### 3.2 用 UI 验证
1. 打开“知识库”页，点击右上角刷新按钮  
2. `本地` 条目点击“入库”  
3. 切换到另一个 Profile（指向另一套 Dify 数据集），应看到对账差异  
4. `DIFY` 条目点击“获取”，获取后应变成可打开的本地笔记

## 4. 已知限制（当前版本）
- 旧的 Dify 文档（没有 `[platform:video_id:created_at_ms]` tag）会显示为 `DIFY(旧)`，暂不支持自动“获取”；需要重新“入库/重入库”生成新格式。
- `DIFY_ONLY_NO_BUNDLE` 表示 Dify 里有条目，但 MinIO 缺原文包：无法“获取”，需要在拥有本地原文的设备上点一次“入库/补传”。
- `DELETED` 表示该条目在当前 Profile 已被 tombstone 标记删除；如需恢复，请在拥有本地原文的设备重新入库。

## 5. 排错（Dify 文档索引 error）
如果你在 Dify 的 Dataset 文档列表里看到 `indexing_status=error`，常见原因是 **Embedding 服务不可达**（例如报错里出现 `...:11434/api/embed` 超时）。

推荐做法（最稳）：把 Ollama 跑在 **同一个 docker-compose 网络**，并在 Dify 里把 Embedding Base URL 配成 `http://ollama:11434`。

服务器示例（假设 Dify compose 项目网络名为 `docker_default`，如不同请按实际替换）：
```bash
docker start ollama || true
docker network connect docker_default ollama || true
docker exec -it ollama ollama list
```
验证（从 Dify 网络内访问 Ollama）：
```bash
docker run --rm --network docker_default curlimages/curl:8.5.0 http://ollama:11434/api/tags
```
然后在 Dify 控制台：Settings → Model Provider → Embeddings，选择 Ollama，并把 Base URL 设为 `http://ollama:11434`，模型选择 `nomic-embed-text`（或你实际 pull 的 embedding 模型），再对 error 文档点击“重试索引/重新索引”。
