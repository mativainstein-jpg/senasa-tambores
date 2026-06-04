@echo off
setlocal

if not exist .venv\Scripts\python.exe (
  echo No existe .venv. Ejecute primero instalar_dependencias.bat
  exit /b 1
)

call .venv\Scripts\activate
python main.py

endlocal
