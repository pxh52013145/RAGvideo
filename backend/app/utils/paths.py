from __future__ import annotations

import os
from pathlib import Path


# backend/app/utils/paths.py -> parents: utils/ -> app/ -> backend/
BACKEND_ROOT = Path(__file__).resolve().parents[2]


def backend_root() -> Path:
    return BACKEND_ROOT


def resolve_path(value: str | None, *, default: str) -> Path:
    """
    Resolve a filesystem path:
    - Absolute paths are used as-is.
    - Relative paths are resolved relative to the backend project root (not CWD).
    """
    raw = (value or "").strip()
    if not raw:
        raw = default
    p = Path(raw).expanduser()
    if p.is_absolute():
        return p
    return (BACKEND_ROOT / p).resolve()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def static_mount_path() -> str:
    return (os.getenv("STATIC") or "/static").strip() or "/static"


def static_dir() -> Path:
    # Allow overriding the on-disk static directory via env for deployments.
    return resolve_path(os.getenv("STATIC_DIR"), default="static")


def uploads_dir() -> Path:
    return resolve_path(os.getenv("UPLOAD_DIR"), default="uploads")


def screenshots_root_dir() -> Path:
    # Historically OUT_DIR defaults to ./static/screenshots.
    return resolve_path(os.getenv("OUT_DIR"), default="static/screenshots")


def note_output_dir() -> Path:
    return resolve_path(os.getenv("NOTE_OUTPUT_DIR"), default="note_results")


def logs_dir() -> Path:
    return resolve_path(os.getenv("LOG_DIR"), default="logs")


def sqlite_db_path() -> Path:
    return resolve_path(os.getenv("SQLITE_DB_PATH"), default="bili_note.db")

