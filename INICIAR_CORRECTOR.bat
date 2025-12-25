@echo off
title Corrector Ortotipografico RAE
color 0B

echo.
echo  =========================================
echo   CORRECTOR ORTOTIPOGRAFICO RAE COMPLETO  
echo  =========================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado.
    echo.
    echo Descarga Python desde: https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

echo  Verificando dependencias...
echo.

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo  Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Instalar dependencias si es necesario
if not exist "venv\installed.flag" (
    echo.
    echo  Instalando dependencias (esto tarda unos minutos)...
    echo.
    pip install -r requirements.txt
    python -m spacy download es_core_news_sm
    echo. > venv\installed.flag
)

echo.
echo  =========================================
echo   Iniciando servidor web...
echo   Abre tu navegador en: http://localhost:5000
echo  =========================================
echo.
echo   Presiona Ctrl+C para cerrar el servidor
echo.

python app_web.py

pause
