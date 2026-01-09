#!/usr/bin/env bash
set -e

# uncomment this for debugging
# set -x

# Switch to repo root (script is located in backend/)
cd "$(dirname "$0")/.."

echo "Current working directory: $(pwd)"

echo "Cleaning previous build outputs..."
rm -rf backend/dist backend/build ./BillNote_frontend/src-tauri/bin/*
echo "Clean done."

TARGET_TRIPLE=$(rustc -Vv | grep host | cut -f2 -d' ')
echo "Detected target triple: $TARGET_TRIPLE"

echo "Preparing .env for bundle..."
TEMP_ENV=0
if [ ! -f .env ]; then
  echo "No .env found, creating a temporary one from .env.example..."
  cp .env.example .env
  TEMP_ENV=1
else
  echo "Found .env, bundling it into the backend sidecar..."
fi

echo "Running PyInstaller..."
pyinstaller \
  --name BiliNoteBackend \
  --paths backend \
  --distpath ./BillNote_frontend/src-tauri/bin \
  --workpath backend/build \
  --specpath backend \
  --hidden-import uvicorn \
  --hidden-import fastapi \
  --hidden-import starlette \
  --add-data "app/db/builtin_providers.json:." \
  --add-data ".env:." \
  "$(pwd)/backend/main.py"

echo "Cleaning temporary .env..."
if [ "$TEMP_ENV" = "1" ]; then
  rm .env
fi

# Rename to include target triple (Tauri sidecar convention).
mv \
  ./BillNote_frontend/src-tauri/bin/BiliNoteBackend/BiliNoteBackend \
  ./BillNote_frontend/src-tauri/bin/BiliNoteBackend/BiliNoteBackend-$TARGET_TRIPLE

echo "PyInstaller build complete."
echo "Output contents:"
ls -l ./BillNote_frontend/src-tauri/bin/BiliNoteBackend

echo "Please check src-tauri/bin/BiliNoteBackend and confirm it contains a .env file."
