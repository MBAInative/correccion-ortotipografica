@echo off
echo ========================================
echo  Construccion del Corrector RAE .exe
echo ========================================
echo.

REM Verificar PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller...
    pip install pyinstaller
)

echo.
echo Creando carpetas necesarias...
if not exist "static" mkdir static
if not exist "sessions" mkdir sessions

echo.
echo Construyendo ejecutable...
echo Esto puede tardar varios minutos...
echo.

pyinstaller --clean corrector_rae.spec

echo.
echo ========================================
if exist "dist\CorrectorRAE.exe" (
    echo  EXITO! Ejecutable creado en:
    echo  dist\CorrectorRAE.exe
    echo.
    echo  Para distribuir, copia toda la carpeta
    echo  'dist' a tu amigo.
) else (
    echo  ERROR: No se pudo crear el ejecutable
    echo  Revisa los mensajes de error arriba.
)
echo ========================================
pause
