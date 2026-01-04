from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import find_dotenv, load_dotenv


def load_dotenv_safely(*, override: bool = False) -> str | None:
    """
    Load `.env` in both dev mode and PyInstaller packaged mode.

    Priority:
    1) DOTENV_PATH (explicit)
    2) find_dotenv(usecwd=True) (walk up from CWD)
    3) .env next to executable
    4) PyInstaller internal `.env` (sys._MEIPASS or `<exe_dir>/_internal/.env`)
    """

    candidates: list[Path] = []

    explicit = (os.getenv("DOTENV_PATH") or "").strip()
    if explicit:
        candidates.append(Path(explicit))

    found = find_dotenv(usecwd=True)
    if found:
        candidates.append(Path(found))

    exe_dir = Path(sys.executable).resolve().parent
    candidates.append(exe_dir / ".env")
    candidates.append(exe_dir / "_internal" / ".env")

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(str(meipass)) / ".env")

    seen: set[str] = set()
    for path in candidates:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        if path.exists():
            load_dotenv(dotenv_path=path, override=override)
            return key

    load_dotenv(override=override)
    return None

