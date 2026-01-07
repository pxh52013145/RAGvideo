import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.utils.paths import ensure_dir, logs_dir

# 日志目录
LOG_DIR = ensure_dir(logs_dir())

# 日志格式
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 控制台输出
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

# 文件输出
max_bytes = int(os.getenv("LOG_MAX_BYTES", "10485760") or "10485760")
backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5") or "5")
file_handler = RotatingFileHandler(
    LOG_DIR / "app.log",
    maxBytes=max(1024 * 1024, max_bytes),
    backupCount=max(1, backup_count),
    encoding="utf-8",
)
file_handler.setFormatter(formatter)

# 获取日志器

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.propagate = False
    return logger
