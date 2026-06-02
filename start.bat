@echo off
title WhiskerShelf - AI Paper Library
color 0E
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

REM ============================================================
REM  WhiskerShelf startup script
REM  - 自动定位 app.py 所在目录
REM  - 把 PDF 所在目录作为"用户数据目录"传给 app.py
REM    (默认是 start.bat 所在目录的上一级, 适合 "release/ 是开发目录" 的常见布局)
REM  - 也可手动指定: set WS_DATA=E:\path\to\papers
REM ============================================================

setlocal
cd /d "%~dp0"

REM 默认 ROOT_DIR = start.bat 的父目录 (即 release/ 的上一层)
if "%WS_DATA%"=="" (
    set "WS_DATA=%~dp0.."
)

echo.
echo  ============================================
echo      WhiskerShelf  AI Paper Library
echo  ============================================
echo.
echo   PDFs data dir : %WS_DATA%
echo   app dir       : %~dp0
echo   browse at     : http://127.0.0.1:8080
echo.
echo   (press Ctrl+C to stop)
echo.

python app.py --root "%WS_DATA%"

echo.
echo  Service stopped.
pause
