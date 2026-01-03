@echo off
setlocal enabledelayedexpansion

REM 切换到脚本所在目录的上级，也就是项目根目录
cd /d %~dp0..
echo 当前工作目录：%cd%

REM 清理旧的构建
echo 清理旧的构建...
if exist backend\dist rmdir /s /q backend\dist
if exist backend\build rmdir /s /q backend\build
if exist BillNote_frontend\src-tauri\bin rmdir /s /q BillNote_frontend\src-tauri\bin
echo 清理完成。

REM 重新创建 Tauri 需要的目录结构
mkdir BillNote_frontend\src-tauri\bin

REM 获取 Rust 的 target triple（适配 Tauri 对应平台）
for /f "tokens=2 delims=:" %%A in ('rustc -Vv ^| findstr "host"') do (
    set "TARGET_TRIPLE=%%A"
)
set "TARGET_TRIPLE=%TARGET_TRIPLE: =%"
echo Detected target triple: %TARGET_TRIPLE%


REM --- 核心修改部分开始 ---

REM 步骤 1: 为了避免 PyInstaller 的解析歧义，我们先手动复制文件
echo 为打包准备 .env 文件...
set "TEMP_ENV=0"
if not exist .env (
  echo æœªæ£€æµ‹åˆ°.envï¼Œç”¨ .env.example åˆ›å»ºä¸´æ—¶ .env...
  copy /Y .env.example .env >nul
  set "TEMP_ENV=1"
) else (
  echo æ£€æµ‹åˆ°.envï¼Œå°†æ‰“åŒ…å½“å‰ .env...
)

REM 步骤 2: 执行 PyInstaller 打包，直接添加已存在的 .env 文件
echo 开始 PyInstaller 打包...
REM Copy .env into backend/.env to match --specpath backend behavior in PyInstaller
copy /Y .env backend\.env >nul
pyinstaller ^
  -y ^
  --name BiliNoteBackend ^
  --paths backend ^
  --distpath BillNote_frontend\src-tauri\bin ^
  --workpath backend\build ^
  --specpath backend ^
  --hidden-import uvicorn ^
  --hidden-import fastapi ^
  --hidden-import starlette ^
  --add-data "app\db\builtin_providers.json;." ^
  --add-data ".env;." ^
  backend\main.py

if errorlevel 1 (
  echo PyInstaller failed.
  del backend\.env >nul 2>nul
  if "%TEMP_ENV%"=="1" del .env >nul 2>nul
  exit /b 1
)

REM 步骤 3: 清理在项目根目录创建的临时 .env 文件
echo 清理临时的 .env 文件...
del backend\.env >nul 2>nul
if "%TEMP_ENV%"=="1" (
  del .env
)

REM --- 核心修改部分结束 ---


REM 重命名生成的可执行文件为符合 Tauri 要求的名称
move /Y BillNote_frontend\src-tauri\bin\BiliNoteBackend\BiliNoteBackend.exe BillNote_frontend\src-tauri\bin\BiliNoteBackend\BiliNoteBackend-%TARGET_TRIPLE%.exe

echo PyInstaller 打包完成：
dir BillNote_frontend\src-tauri\bin\BiliNoteBackend

echo 请检查 BillNote_frontend\src-tauri\bin\BiliNoteBackend 目录，确认其中包含了名为 .env 的【文件】。

endlocal
