@echo off
setlocal

echo ============================================================
echo Instalacion de dependencias - SENASA Tambores
echo ============================================================

py -3.12 -m venv .venv
if errorlevel 1 goto error

call .venv\Scripts\activate
if errorlevel 1 goto error

python -m pip install --upgrade pip
if errorlevel 1 goto error

pip install -r requirements.txt
if errorlevel 1 goto error

python -m playwright install chromium
if errorlevel 1 goto error

echo.
echo OK: dependencias instaladas.
goto end

:error
echo.
echo ERROR: La instalacion fallo.
exit /b 1

:end
endlocal
