@echo off
title AI Surveillance System
echo ================================================
echo   AI-Powered Surveillance System
echo   GSCWU - Dept. of Computer Science
echo   Supervisor: Dr. Amna Ikram
echo ================================================
echo.

:: Check if venv exists
if not exist "venv\Scripts\activate" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate venv
call venv\Scripts\activate

:: Check if packages are installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Installing required packages...
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    pip install -r requirements.txt
)

echo.
echo Starting dashboard...
echo Open your browser at: http://localhost:8501
echo.
streamlit run app.py
pause