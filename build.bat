@echo off
setlocal

echo ==============================================
echo   Building Browser Profile Manager
echo ==============================================

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python was not found on PATH.
    exit /b 1
)

echo.
echo [1/3] Creating virtual environment (.venv) if needed...
if not exist ".venv" (
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo.
echo [2/3] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [3/3] Building executable...
pyinstaller --noconfirm --clean ^
    --name "BrowserProfileManager" ^
    --onefile ^
    --windowed ^
    --icon "icons\app_icon(5).ico" ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --add-data "icons;icons" ^
    app.py

echo.
if exist "dist\BrowserProfileManager.exe" (
    echo ==============================================
    echo Build Successful!
    echo EXE: dist\BrowserProfileManager.exe
    echo ==============================================
) else (
    echo Build Failed.
)

endlocal