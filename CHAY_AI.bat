@echo off
setlocal
echo Dang khoi dong AI Story Agent...
echo.

:: Path to the project in WSL
set WSL_PATH=/home/thuongnh29/AIET

:: Check if WSL is installed
wsl --status >nul 2>&1
if %errorlevel% neq 0 (
    echo [LOI] WSL chua duoc cai dat hoac khong hoat dong.
    pause
    exit /b 1
)

:: Run the server in WSL
wsl -d Ubuntu-24.04 -e bash -c "cd %WSL_PATH% && export PYTHONPATH=$PYTHONPATH:$(pwd)/src && poetry run python src/app/main.py"

if %errorlevel% neq 0 (
    echo.
    echo [LOI] Co loi xay ra khi khoi dong server.
    pause
)
