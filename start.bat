@echo off
title WhiskerShelf - AI Paper Library
color 0E
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

REM ============================================================
REM  WhiskerShelf startup script
REM  - 自动 cd 到 start.bat 所在目录
REM  - 该目录下必须有 app.py + static/ + 你的 PDF 文件
REM  - 高级用户可手动指定 ROOT: python app.py --root "E:\my-papers"
REM ============================================================

setlocal
cd /d "%~dp0"

echo.
echo  ============================================
echo      WhiskerShelf  AI Paper Library
echo  ============================================
echo.
echo   Working dir : %CD%
echo   Browse at   : http://127.0.0.1:8080
echo.
echo   (press Ctrl+C to stop)
echo.

python app.py

echo.
echo  Service stopped.
pause
