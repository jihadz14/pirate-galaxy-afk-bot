@echo off
chcp 65001 >nul
title Pirate Galaxy Bot - Original
color 0A

echo.
echo ╔═══════════════════════════════════════╗
echo ║   PIRATE GALAXY BOT - ORIGINAL       ║
echo ║   Made by Jihadz                     ║
echo ╚═══════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no está instalado o no está en PATH
    echo.
    echo Descarga Python desde: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Verificar archivo principal
if not exist "PGBot.py" (
    echo [ERROR] No se encuentra PGBot.py
    echo.
    echo Asegúrate de estar en la carpeta correcta del bot.
    echo.
    pause
    exit /b 1
)

REM Verificar estructura
if not exist "core\bot.py" (
    echo [ADVERTENCIA] Estructura de carpetas no encontrada
    echo.
    echo Ejecutando organize_files.bat...
    call organize_files.bat
    echo.
    echo Por favor, ejecuta run_original.bat nuevamente.
    pause
    exit /b 1
)

echo [INFO] Iniciando bot versión original...
echo [INFO] Presiona Q para salir, P para pausar
echo.
echo ════════════════════════════════════════
echo.

python PGBot.py

echo.
echo ════════════════════════════════════════
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] El bot se cerró con errores (código: %errorlevel%)
    echo.
    echo Posibles causas:
    echo - Faltan dependencias (ejecuta install_dependencies.bat)
    echo - Pirate Galaxy no está abierto
    echo - Faltan imágenes de referencia en data/images/
) else (
    echo.
    echo [OK] Bot cerrado correctamente
)
echo.
pause