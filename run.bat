@echo off
title Face & Gait Recognition - Setup & Run

echo ============================================
echo  Face & Gait Recognition Surveillance App
echo ============================================
echo.

:: Check Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

echo [1/2] Installing required packages...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install packages.
    echo Try running this file as Administrator.
    pause
    exit /b 1
)

echo [2/2] Starting app...
echo.
python app.py

pause
