@echo off
chcp 65001 >nul
title Pirate Galaxy Bot - Original (Eclip5e)
color 0A

echo.
echo ╔═══════════════════════════════════════╗
echo ║   PIRATE GALAXY BOT - ORIGINAL       ║
echo ║   Made by Eclip5e                    ║
echo ╚═══════════════════════════════════════╝
echo.

REM Ir a la raíz del proyecto
cd /d "%~dp0.."

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
if not exist "main.py" (
    echo [ERROR] No se encuentra main.py
    echo.
    echo Asegúrate de estar en la carpeta correcta del bot.
    echo.
    pause
    exit /b 1
)

REM Verificar estructura
if not exist "src\bot\bot_core.py" (
    echo [ERROR] Estructura de carpetas incorrecta
    echo.
    echo Asegúrate de que la carpeta src/bot/ existe con todos los archivos.
    echo.
    pause
    exit /b 1
)

echo [INFO] Iniciando bot versión original (Eclip5e)...
echo [INFO] Presiona Q para salir, P para pausar
echo.
echo ════════════════════════════════════════
echo.

python main.py

echo.
echo ════════════════════════════════════════
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] El bot se cerró con errores (código: %errorlevel%)
    echo.
    echo Posibles causas:
    echo - Faltan dependencias (ejecuta scripts\install_dependencies.bat)
    echo - Pirate Galaxy no está abierto
    echo - Faltan imágenes de referencia en data/images/
) else (
    echo.
    echo [OK] Bot cerrado correctamente
)
echo.
pause
