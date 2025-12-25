@echo off
chcp 65001 >nul
title Corrector Ortotipografico RAE
color 0A

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║     CORRECTOR ORTOTIPOGRAFICO RAE                         ║
echo  ║     Copyright 2025 - Luis Benedicto Tuzon                 ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

:: Verificar instalacion
if not exist "venv" (
    echo  ERROR: Primero ejecuta INSTALAR.bat
    pause
    exit /b 1
)

:: Activar entorno
call venv\Scripts\activate.bat

echo  Iniciando servidor web...
echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║  SERVIDOR INICIADO                                        ║
echo  ║                                                           ║
echo  ║  Abre tu navegador en:                                    ║
echo  ║  http://localhost:5000                                    ║
echo  ║                                                           ║
echo  ║  Para cerrar: Ctrl+C o cierra esta ventana                ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

python app_web.py

pause
