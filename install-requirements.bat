@echo off
cls

:: Step 1: Check if Python is installed
python --version 2>NUL
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b 1
)

:: Step 2: Install required Python packages
pip install yt-dlp openai requests

:: Step 3: Exit the batch script
exit /b 0
