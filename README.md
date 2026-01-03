# RAG 视频（RAGVideo）

基于 BiliNote 改造的「RAG 视频知识库」项目：视频转写与笔记生成后，自动写入 Dify Knowledge（Dataset），再通过 Dify App 完成对话式检索与问答，并返回引用片段（含时间戳）。

## 架构说明

- 本项目后端（FastAPI）：视频下载/解析 → 转写 → 生成 Markdown 笔记 → 将“笔记 + 带时间戳的转写”写入 Dify Dataset → 代理 Dify Chat API
- 本项目前端（Vite/React + 可选 Tauri）：入库（通过“生成笔记”触发）/任务状态/对话与引用展示
- Dify：负责知识库向量检索、RAG/工作流、模型配置与 API Key 管理

## 运行前准备

- Docker Desktop（用于自建 Dify；如果你有现成的 Dify，可跳过）
- FFmpeg（必须，确保 `ffmpeg -version` 可用）
- Python 3.10+（建议 3.10/3.11，64-bit）
- Node.js 18+（建议 18/20）+ pnpm（建议 `corepack enable`）

> 不强制安装 Ollama：Dify 的模型提供商可以选 DeepSeek / OpenAI / 其它兼容 OpenAI 的 API。

## 1) 自建 Dify（一次性）

按 Dify 官方自建文档用 Docker 启动即可（建议使用 Dify 的官方 docker-compose 部署方式）。

启动后访问 Dify 控制台，完成两件事：

1. **创建 Dataset（知识库）**：Knowledge → New Dataset
2. **创建 App（用于对话）**：Studio → New App（Chat/Workflow 均可），打开检索能力并发布（Publish）

## 2) 准备 Dify 配置（必须）

本项目需要 4 个值（都在 Dify 控制台可找到）：

- `DIFY_BASE_URL`：你的 Dify 地址（不要带 `/v1`），例如 `http://localhost` 或 `https://xxxx.trycloudflare.com`
- `DIFY_DATASET_ID`：Dataset 的 UUID（可从 Dataset 页面 URL 里取）
- `DIFY_SERVICE_API_KEY`：用于写入 Knowledge 的 Key（常见前缀是 `dataset-`）
- `DIFY_APP_API_KEY`：用于对话检索的 App Key（常见前缀是 `app-`）

## 3) 配置项目 `.env`

在项目根目录：

```powershell
Copy-Item .env.example .env
notepad .env
```

至少填写/确认：

- `DIFY_BASE_URL`
- `DIFY_DATASET_ID`
- `DIFY_SERVICE_API_KEY`
- `DIFY_APP_API_KEY`
- （本地开发建议）`VITE_DEV_PROXY_TARGET=http://127.0.0.1:8483`

## 4) 启动后端（开发模式）

建议在**项目根目录**运行（确保读取根目录的 `.env`）：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python backend\main.py
```

验证：`http://127.0.0.1:8483/docs`

## 5) 启动前端（开发模式）

另开一个终端：

```powershell
cd BillNote_frontend
corepack enable
pnpm install
pnpm dev
```

打开：`http://localhost:3015`

> `pnpm dev` 是 Web 开发模式，不会弹桌面窗口；桌面端见第 7 节。

## 6) 使用方式（RAG 入库 & 问答）

1. 在界面里选择/填写视频来源（B 站/YouTube/本地视频等），点击 **生成笔记**
2. 任务完成后会：
   - 在本地保存 Markdown 笔记到 `note_results/`
   - 自动把“笔记 + 带 `[TIME=mm:ss-mm:ss]` 标记的转写内容”写入 Dify Dataset（用于 RAG 检索）
3. 切到 **RAG 问答** 页面直接提问：右侧会显示引用片段（包含时间戳，可用于定位片段）

## 7) （可选）桌面端打包（Tauri）

前置：安装 Rust + VS Build Tools（Desktop C++）。

1. 构建后端 sidecar：

```powershell
cd backend
.\build.bat
```

2. 打包前端：

```powershell
cd ..\BillNote_frontend
pnpm tauri build
```

产物在 `BillNote_frontend\src-tauri\target\release\`（或对应 profile 目录）

或者 `pnpm tauri dev启动tauri桌面端`。

## 常见问题

- Dify 报 `Workflow not published`：去 Dify 把 App **Publish** 后再调用
- Dify 报 `Model ... credentials is not initialized`：去 Dify 的模型提供商里把 LLM/Embedding 配好，并在 App 中选择正确模型
- FFmpeg 找不到：把 ffmpeg 加入 PATH，或在 `.env` 里填写 `FFMPEG_BIN_PATH=...\\ffmpeg.exe`
- 中文路径/中文文件名导致处理失败：尽量把项目目录和视频文件名改成英文/数字
