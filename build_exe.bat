@echo off
setlocal

echo ============================================================
echo Construccion de EXE - SENASA Tambores
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

pyinstaller ^
  --clean ^
  --onefile ^
  --name SENASA_Tambores ^
  --collect-all playwright ^
  main.py
if errorlevel 1 goto error

echo.
echo OK: EXE generado en dist\SENASA_Tambores.exe
echo Copie Tambores.xlsx junto al EXE antes de ejecutarlo.
goto end

:error
echo.
echo ERROR: La construccion fallo.
exit /b 1

:end
endlocal
