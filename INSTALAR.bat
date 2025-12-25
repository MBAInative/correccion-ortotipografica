@echo off
chcp 65001 >nul
title Corrector Ortotipografico RAE - Instalador
color 0B

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║     CORRECTOR ORTOTIPOGRAFICO RAE - INSTALADOR            ║
echo  ║     Copyright 2025 - Luis Benedicto Tuzon                 ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  ╔═══════════════════════════════════════════════════════════╗
    echo  ║  ERROR: Python no esta instalado                          ║
    echo  ║                                                           ║
    echo  ║  Por favor:                                               ║
    echo  ║  1. Ve a https://www.python.org/downloads/                ║
    echo  ║  2. Descarga Python 3.11 o superior                       ║
    echo  ║  3. IMPORTANTE: Marca "Add Python to PATH"                ║
    echo  ║  4. Reinicia este instalador                              ║
    echo  ╚═══════════════════════════════════════════════════════════╝
    echo.
    pause
    exit /b 1
)

echo  [1/4] Python detectado correctamente
echo.

:: Crear entorno virtual
if not exist "venv" (
    echo  [2/4] Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo  ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
) else (
    echo  [2/4] Entorno virtual ya existe
)
echo.

:: Activar entorno e instalar dependencias
echo  [3/4] Instalando dependencias (puede tardar 5-10 minutos)...
echo         Por favor espere...
echo.
call venv\Scripts\activate.bat

:: Verificar si ya están instaladas
pip show flask >nul 2>&1
if errorlevel 1 (
    pip install --quiet flask lxml werkzeug jinja2 spacy
    python -m spacy download es_core_news_sm
) else (
    echo         Dependencias ya instaladas
)
echo.

echo  [4/4] Instalacion completada!
echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║  INSTALACION EXITOSA                                      ║
echo  ║                                                           ║
echo  ║  Para INICIAR el corrector:                               ║
echo  ║  - Ejecuta: INICIAR.bat                                   ║
echo  ║                                                           ║
echo  ║  Luego abre tu navegador en:                              ║
echo  ║  http://localhost:5000                                    ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.
pause
