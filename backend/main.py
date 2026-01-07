import os
from contextlib import asynccontextmanager

from dotenv_loader import load_dotenv_safely

load_dotenv_safely()

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.db.init_db import init_db
from app.db.provider_dao import seed_default_providers
from app.exceptions.exception_handlers import register_exception_handlers
# from app.db.model_dao import init_model_table
# from app.db.provider_dao import init_provider_table
from app.utils.logger import get_logger
from app import create_app
from app.transcriber.transcriber_provider import get_transcriber
from app.utils.paths import ensure_dir, screenshots_root_dir, static_dir as get_static_dir, static_mount_path, uploads_dir as get_uploads_dir
from events import register_handler
from ffmpeg_helper import ensure_ffmpeg_or_raise

logger = get_logger(__name__)

# 读取 .env 中的路径（相对路径统一按 backend 根目录解析，避免因启动目录不同而生成两套数据）
static_path = static_mount_path()
static_dir = ensure_dir(get_static_dir())
uploads_dir = ensure_dir(get_uploads_dir())
out_dir = ensure_dir(screenshots_root_dir())

@asynccontextmanager
async def lifespan(app: FastAPI):
    register_handler()
    init_db()
    get_transcriber(transcriber_type=os.getenv("TRANSCRIBER_TYPE", "fast-whisper"))
    seed_default_providers()
    yield

app = create_app(lifespan=lifespan)
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://tauri.localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  #  加上 Tauri 的 origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)
app.mount(static_path, StaticFiles(directory=str(static_dir)), name="static")
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")









if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 8483))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, reload=False)
