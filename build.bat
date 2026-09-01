@echo off
REM Script para compilar el proyecto en ejecutable
REM YouTube MP3 Downloader

echo ========================================
echo Compilando YouTube MP3 Downloader...
echo ========================================

REM Borrar el ejecutable anterior si existe
if exist "dist\main.exe" (
    echo Borrando ejecutable anterior...
    del /F /Q "dist\main.exe"
)

REM Borrar directorio build si existe
if exist "build" (
    echo Borrando directorio build anterior...
    rmdir /S /Q "build"
)

REM Compilar con PyInstaller
echo Iniciando compilacion con PyInstaller...
.venv\Scripts\pyinstaller.exe --onefile --windowed --icon=icon.ico --add-data "icon.ico;." --add-data "logo.png;." --add-data "src;src" main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Compilacion exitosa!
    echo Ejecutable creado en: dist\main.exe
    echo ========================================
    echo.
    echo NOTA: El historial de descargas se creara
    echo automaticamente en el directorio del ejecutable
    echo cuando se ejecute la aplicacion.
) else (
    echo.
    echo ========================================
    echo ERROR en la compilacion
    echo ========================================
)

pause
