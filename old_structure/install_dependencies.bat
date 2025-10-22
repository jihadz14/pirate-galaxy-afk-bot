@echo off
chcp 65001 >nul
title Instalador de Dependencias - PG Bot
color 0E

echo.
echo ╔═══════════════════════════════════════════════╗
echo ║   INSTALADOR DE DEPENDENCIAS - PG BOT        ║
echo ╚═══════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no está instalado
    echo.
    echo Descarga Python desde: https://www.python.org/downloads/
    echo IMPORTANTE: Marca la opción "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo Python detectado: 
python --version
echo.

echo ════════════════════════════════════════════════
echo   Instalando dependencias...
echo ════════════════════════════════════════════════
echo.

echo [1/8] Actualizando pip...
python -m pip install --upgrade pip setuptools wheel --quiet
if %errorlevel% neq 0 (
    echo ✗ Error al actualizar pip
    pause
    exit /b 1
)
echo ✓ pip actualizado

echo [2/8] Instalando pyautogui...
pip install pyautogui --quiet
if %errorlevel% neq 0 (
    echo ✗ Error instalando pyautogui
) else (
    echo ✓ pyautogui instalado
)

echo [3/8] Instalando keyboard...
pip install keyboard --quiet
if %errorlevel% neq 0 (
    echo ✗ Error instalando keyboard
) else (
    echo ✓ keyboard instalado
)

echo [4/8] Instalando colorama...
pip install colorama --quiet
if %errorlevel% neq 0 (
    echo ✗ Error instalando colorama
) else (
    echo ✓ colorama instalado
)

echo [5/8] Instalando pytesseract y opencv...
pip install pytesseract opencv-python --quiet
if %errorlevel% neq 0 (
    echo ✗ Error instalando pytesseract/opencv
) else (
    echo ✓ pytesseract y opencv instalados
)

echo [6/8] Instalando pywin32...
pip install pywin32 --quiet
if %errorlevel% neq 0 (
    echo ✗ Error instalando pywin32
) else (
    echo ✓ pywin32 instalado
)

echo [7/8] Configurando pywin32...
python -m pywin32_postinstall -install >nul 2>&1
echo ✓ pywin32 configurado

echo [8/8] Instalando PyQt5 (para versión mejorada)...
pip install PyQt5 PyQtChart --quiet
if %errorlevel% neq 0 (
    echo ⚠ PyQt5 no instalado (solo para versión mejorada)
) else (
    echo ✓ PyQt5 instalado
)

echo.
echo ════════════════════════════════════════════════
echo   Verificando instalación...
echo ════════════════════════════════════════════════
echo.

python -c "import pyautogui; print('✓ pyautogui')" 2>nul || echo ✗ pyautogui
python -c "import keyboard; print('✓ keyboard')" 2>nul || echo ✗ keyboard
python -c "import colorama; print('✓ colorama')" 2>nul || echo ✗ colorama
python -c "import cv2; print('✓ opencv')" 2>nul || echo ✗ opencv
python -c "import pytesseract; print('✓ pytesseract')" 2>nul || echo ✗ pytesseract
python -c "import win32api; print('✓ pywin32')" 2>nul || echo ✗ pywin32
python -c "from PyQt5.QtWidgets import QApplication; print('✓ PyQt5')" 2>nul || echo ⚠ PyQt5 (opcional)

echo.
echo ════════════════════════════════════════════════
echo   ✓ INSTALACIÓN COMPLETADA
echo ════════════════════════════════════════════════
echo.
echo Todas las dependencias están listas.
echo.
echo IMPORTANTE:
echo - Instala Tesseract OCR desde:
echo   https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo - Configura la ruta en core/settings.json
echo.
pause