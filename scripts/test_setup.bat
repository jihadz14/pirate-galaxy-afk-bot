@echo off
chcp 65001 >nul
title Verificación de Configuración - Pirate Galaxy Bot
color 0E

echo.
echo ╔═══════════════════════════════════════╗
echo ║   VERIFICACIÓN DE CONFIGURACIÓN      ║
echo ║   Pirate Galaxy Bot                  ║
echo ╚═══════════════════════════════════════╝
echo.

REM Ir a la raíz del proyecto
cd /d "%~dp0.."

echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python NO está instalado
    echo.
    echo Instala Python desde: https://www.python.org/downloads/
    goto :error
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo ✓ !PYTHON_VERSION! detectado
)

echo.
echo [2/6] Verificando estructura de archivos...
set ERROR_COUNT=0

if not exist "main.py" (
    echo ✗ main.py NO encontrado
    set /a ERROR_COUNT+=1
) else (
    echo ✓ main.py
)

if not exist "main_enhanced.py" (
    echo ✗ main_enhanced.py NO encontrado
    set /a ERROR_COUNT+=1
) else (
    echo ✓ main_enhanced.py
)

if not exist "config\settings.json" (
    echo ✗ config\settings.json NO encontrado
    set /a ERROR_COUNT+=1
) else (
    echo ✓ config\settings.json
)

if not exist "src\bot\bot_core.py" (
    echo ✗ src\bot\bot_core.py NO encontrado
    set /a ERROR_COUNT+=1
) else (
    echo ✓ src\bot\bot_core.py
)

if not exist "data\images" (
    echo ✗ data\images\ NO encontrado
    set /a ERROR_COUNT+=1
) else (
    echo ✓ data\images\
)

if %ERROR_COUNT% gtr 0 (
    echo.
    echo ✗ %ERROR_COUNT% archivo(s) faltante(s)
    goto :error
)

echo.
echo [3/6] Verificando dependencias básicas...
python -c "import pyautogui" >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ pyautogui NO instalado
    set MISSING_DEPS=1
) else (
    echo ✓ pyautogui
)

python -c "import keyboard" >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ keyboard NO instalado
    set MISSING_DEPS=1
) else (
    echo ✓ keyboard
)

python -c "import colorama" >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ colorama NO instalado
    set MISSING_DEPS=1
) else (
    echo ✓ colorama
)

python -c "import cv2" >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ opencv-python NO instalado
    set MISSING_DEPS=1
) else (
    echo ✓ opencv-python
)

python -c "import pytesseract" >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ pytesseract NO instalado
    set MISSING_DEPS=1
) else (
    echo ✓ pytesseract
)

if defined MISSING_DEPS (
    echo.
    echo ⚠ Algunas dependencias faltan
    echo.
    echo Ejecuta: pip install pyautogui keyboard colorama opencv-python pytesseract pywin32
    echo.
    echo O ejecuta: scripts\install_dependencies.bat
    set /p INSTALL="¿Instalar ahora? (s/n): "
    if /i "!INSTALL!"=="s" (
        echo.
        echo Instalando dependencias...
        pip install pyautogui keyboard colorama opencv-python pytesseract pywin32
        echo.
    )
)

echo.
echo [4/6] Verificando dependencias Enhanced (PyQt5)...
python -c "from PyQt5.QtWidgets import QApplication" >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ PyQt5 NO instalado (necesario para main_enhanced.py)
    echo.
    echo   Para usar la versión Enhanced, instala:
    echo   pip install PyQt5 PyQtChart
) else (
    echo ✓ PyQt5 instalado
)

echo.
echo [5/6] Probando sintaxis de archivos Python...
python -m py_compile main.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ main.py tiene errores de sintaxis
    goto :error
) else (
    echo ✓ main.py sintaxis correcta
)

python -m py_compile main_enhanced.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ main_enhanced.py tiene errores de sintaxis
    goto :error
) else (
    echo ✓ main_enhanced.py sintaxis correcta
)

echo.
echo [6/6] Verificando Tesseract OCR...
where tesseract >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠ Tesseract NO encontrado en PATH
    echo.
    echo   Verifica que la ruta en config\settings.json sea correcta
    echo   O descarga desde: https://github.com/UB-Mannheim/tesseract/wiki
) else (
    for /f "tokens=*" %%i in ('tesseract --version 2^>^&1 ^| findstr /r "^tesseract"') do (
        echo ✓ %%i
    )
)

echo.
echo ════════════════════════════════════════
echo.
echo ✅ VERIFICACIÓN COMPLETADA
echo.
echo Tu bot está listo para ejecutar:
echo.
echo   Versión Original:  scripts\run_original.bat
echo   Versión Enhanced:  scripts\run_enhanced.bat
echo.
echo ════════════════════════════════════════
echo.
pause
exit /b 0

:error
echo.
echo ════════════════════════════════════════
echo.
echo ❌ VERIFICACIÓN FALLÓ
echo.
echo Por favor, revisa los errores arriba y corrígelos.
echo.
echo ════════════════════════════════════════
echo.
pause
exit /b 1
