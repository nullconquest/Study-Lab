@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Creating Hector Study Lab environment...
  py -3 -m venv .venv
  if errorlevel 1 (
    echo Install Python 3.11 or newer from python.org, then run this again.
    pause
    exit /b 1
  )
)
if not exist ".venv\forge-installed.txt" (
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo Installation did not complete. Check your internet connection and try again.
    pause
    exit /b 1
  )
  echo installed>".venv\forge-installed.txt"
)
".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1
pause
