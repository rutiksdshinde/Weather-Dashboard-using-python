@echo off
echo ========================================
echo   Weather Dashboard - India
echo ========================================
echo.
echo Starting the Weather Dashboard server...
echo Open your browser and go to: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the application
python app.py

pause