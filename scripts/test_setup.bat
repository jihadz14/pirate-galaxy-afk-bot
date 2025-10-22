@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Verificación - Pirate Galaxy Bot
color 0E

echo.
echo ========================================
echo   VERIFICACION DE CONFIGURACION
echo   Pirate Galaxy Bot
echo ========================================
echo.

REM Ir a la raíz del proyecto
cd /d "%~dp0.."

echo [1/6] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python NO esta instalado
    echo.
    echo Instala Python desde: https://www.python.org/downloads/
    echo.
    goto :error
) else (
    python --version
    echo OK - Python detectado
)

echo.
echo [2/6] Verificando estructura de archivos...
set ERROR_COUNT=0

if not exist "main.py" (
    echo X main.py NO encontrado
    set /a ERROR_COUNT+=1
) else (
    echo OK - main.py
)

if not exist "main_enhanced.py" (
    echo X main_enhanced.py NO encontrado
    set /a ERROR_COUNT+=1
) else (
    echo OK - main_enhanced.py
)

if not exist "config\settings.json" (
    echo X config\settings.json NO encontrado
    set /a ERROR_COUNT+=1
) else (
    echo OK - config\settings.json
)

if not exist "src\bot\bot_core.py" (
    echo X src\bot\bot_core.py NO encontrado
    set /a ERROR_COUNT+=1
) else (
    echo OK - src\bot\bot_core.py
)

if !ERROR_COUNT! gtr 0 (
    echo.
    echo X !ERROR_COUNT! archivo(s) faltante(s)
    goto :error
)

echo.
echo [3/6] Verificando dependencias basicas...
set MISSING_DEPS=0

python -c "import pyautogui" >nul 2>&1
if errorlevel 1 (
    echo X pyautogui NO instalado
    set MISSING_DEPS=1
) else (
    echo OK - pyautogui
)

python -c "import keyboard" >nul 2>&1
if errorlevel 1 (
    echo X keyboard NO instalado
    set MISSING_DEPS=1
) else (
    echo OK - keyboard
)

python -c "import colorama" >nul 2>&1
if errorlevel 1 (
    echo X colorama NO instalado
    set MISSING_DEPS=1
) else (
    echo OK - colorama
)

python -c "import cv2" >nul 2>&1
if errorlevel 1 (
    echo X opencv-python NO instalado
    set MISSING_DEPS=1
) else (
    echo OK - opencv-python
)

python -c "import pytesseract" >nul 2>&1
if errorlevel 1 (
    echo X pytesseract NO instalado
    set MISSING_DEPS=1
) else (
    echo OK - pytesseract
)

if !MISSING_DEPS! equ 1 (
    echo.
    echo ! Algunas dependencias faltan
    echo.
    echo Para instalar:
    echo pip install pyautogui keyboard colorama opencv-python pytesseract pywin32
    echo.
    set /p INSTALL="Instalar ahora? (s/n): "
    if /i "!INSTALL!"=="s" (
        echo.
        echo Instalando dependencias...
        pip install pyautogui keyboard colorama opencv-python pytesseract pywin32
        echo.
    )
)

echo.
echo [4/6] Verificando PyQt5 (para version Enhanced)...
python -c "from PyQt5.QtWidgets import QApplication" >nul 2>&1
if errorlevel 1 (
    echo ! PyQt5 NO instalado (solo necesario para main_enhanced.py)
    echo   Para instalar: pip install PyQt5 PyQtChart
) else (
    echo OK - PyQt5 instalado
)

echo.
echo [5/6] Probando sintaxis de archivos Python...
python -m py_compile main.py >nul 2>&1
if errorlevel 1 (
    echo X main.py tiene errores de sintaxis
    goto :error
) else (
    echo OK - main.py sintaxis correcta
)

python -m py_compile main_enhanced.py >nul 2>&1
if errorlevel 1 (
    echo X main_enhanced.py tiene errores de sintaxis
    goto :error
) else (
    echo OK - main_enhanced.py sintaxis correcta
)

echo.
echo [6/6] Verificando Tesseract OCR...
where tesseract >nul 2>&1
if errorlevel 1 (
    echo ! Tesseract NO encontrado en PATH
    echo   Verifica la ruta en config\settings.json
    echo   O descarga desde: https://github.com/UB-Mannheim/tesseract/wiki
) else (
    tesseract --version 2>&1 | findstr /r "^tesseract"
    echo OK - Tesseract detectado
)

echo.
echo ========================================
echo.
echo   VERIFICACION COMPLETADA
echo.
echo Tu bot esta listo para ejecutar:
echo.
echo   Version Original:  scripts\run_original.bat
echo   Version Enhanced:  scripts\run_enhanced.bat
echo.
echo ========================================
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo.
echo   VERIFICACION FALLO
echo.
echo Por favor, revisa los errores arriba.
echo.
echo ========================================
echo.
pause
exit /b 1
