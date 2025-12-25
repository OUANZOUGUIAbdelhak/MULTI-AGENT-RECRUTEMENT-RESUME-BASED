@echo off
echo ========================================
echo Multi-Agent Candidate Selection System
echo Quick Start Script
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo.
echo Checking dependencies...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
) else (
    echo Python dependencies already installed.
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Choose an option:
echo 1. Start Backend API (for React frontend)
echo 2. Start Streamlit Interface
echo 3. Install Frontend Dependencies
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting Backend API...
    echo Backend will be available at http://localhost:8000
    echo.
    python backend_api.py
) else if "%choice%"=="2" (
    echo.
    echo Starting Streamlit Interface...
    echo Interface will be available at http://localhost:8501
    echo.
    streamlit run src/app/app.py
) else if "%choice%"=="3" (
    echo.
    echo Installing Frontend Dependencies...
    cd frontend
    call npm install
    cd ..
    echo.
    echo Frontend dependencies installed!
    echo Run 'npm run dev' in the frontend folder to start the frontend.
) else (
    echo.
    echo Exiting...
    exit /b
)

pause

