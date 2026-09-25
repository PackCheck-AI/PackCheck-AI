@echo off
title PackCheck AI - Startup

echo.
echo ============================================================
echo                    PACKCHECK AI
echo ============================================================
echo.

REM Go to the folder where this BAT file is located
cd /d "%~dp0"

echo [1/3] Activating Python environment...
call sih_env\Scripts\activate.bat

if errorlevel 1 (
    echo.
    echo ❌ ERROR: Could not activate sih_env
    echo Make sure the sih_env folder exists inside SIH_PackCheck.
    echo.
    pause
    exit /b 1
)

echo ✅ sih_env activated.
echo.

echo [2/3] Starting API Server...
start "PackCheck API Server" cmd /k "call sih_env\Scripts\activate.bat && python api\server.py"

timeout /t 2 /nobreak >nul

echo [3/3] Starting Streamlit...
start "PackCheck Streamlit" cmd /k "call sih_env\Scripts\activate.bat && python -m streamlit run app.py"

echo.
echo ============================================================
echo                 PACKCHECK AI STARTED
echo ============================================================
echo.
echo Python Env  : sih_env
echo API Server  : http://localhost:8000
echo Streamlit   : http://localhost:8501
echo.
echo ============================================================
echo.

timeout /t 5 /nobreak >nul
exit