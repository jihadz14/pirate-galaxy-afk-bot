@echo off
chcp 65001 >nul
title Pirate Galaxy Bot - Enhanced
color 0B

echo.
echo ╔═══════════════════════════════════════╗
echo ║   PIRATE GALAXY BOT - ENHANCED       ║
echo ║   UI Gráfica + OCR Mejorado          ║
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
if not exist "main_enhanced.py" (
    echo [ERROR] No se encuentra main_enhanced.py
    echo.
    echo Asegúrate de estar en la carpeta correcta del bot.
    echo.
    pause
    exit /b 1
)

REM Verificar PyQt5
python -c "from PyQt5.QtWidgets import QApplication" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PyQt5 no está instalado
    echo.
    echo Instalando dependencias...
    python -m pip install PyQt5 PyQtChart opencv-python --quiet
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudieron instalar las dependencias
        echo.
        echo Ejecuta manualmente: pip install PyQt5 PyQtChart opencv-python
        pause
        exit /b 1
    )
    echo ✓ Dependencias instaladas
    echo.
)

REM Verificar estructura
if not exist "src\ui\bot_window.py" (
    echo [ERROR] Estructura de carpetas incorrecta
    echo.
    echo Asegúrate de que la carpeta src/ui/ existe con todos los archivos.
    echo.
    pause
    exit /b 1
)

echo [INFO] Iniciando bot versión mejorada...
echo [INFO] Se abrirá una ventana gráfica
echo.
echo ════════════════════════════════════════
echo.

python main_enhanced.py

echo.
echo ════════════════════════════════════════
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] El bot se cerró con errores (código: %errorlevel%)
    echo.
    echo Posibles causas:
    echo - Faltan dependencias (ejecuta install_dependencies.bat)
    echo - PyQt5 no instalado correctamente
    echo - Pirate Galaxy no está abierto
) else (
    echo.
    echo [OK] Bot cerrado correctamente
    echo.
    echo Estadísticas guardadas en: logs/stats.json
)
echo.
pause
