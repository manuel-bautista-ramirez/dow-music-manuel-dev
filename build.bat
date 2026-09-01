@echo off
REM Script para compilar el proyecto en ejecutable y generar instalador
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

REM Borrar instalador anterior si existe
if exist "dist\YouTube_MP3_Downloader_Setup.exe" (
    echo Borrando instalador anterior...
    del /F /Q "dist\YouTube_MP3_Downloader_Setup.exe"
)

REM Compilar con PyInstaller
echo Iniciando compilacion con PyInstaller...
.venv\Scripts\pyinstaller.exe --onefile --windowed --icon=icon.ico --add-data "icon.ico;." --add-data "logo.png;." --add-data "src;src" main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo ERROR en la compilacion con PyInstaller
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo Compilacion exitosa!
echo Ejecutable creado en: dist\main.exe
echo ========================================
echo.

REM Generar instalador con NSIS
echo Generando instalador con NSIS...
echo.

REM Verificar si makensis está disponible
where makensis >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo ERROR: NSIS (makensis) no encontrado
    echo ========================================
    echo.
    echo Para generar el instalador, necesitas instalar NSIS:
    echo 1. Descarga NSIS desde: https://nsis.sourceforge.io/Download
    echo 2. Instala NSIS en tu sistema
    echo 3. Asegurate de que makensis esté en el PATH
    echo.
    echo El ejecutable se ha creado exitosamente en: dist\main.exe
    echo Puedes usarlo directamente sin el instalador.
    echo ========================================
    pause
    exit /b 1
)

REM Ejecutar makensis para crear el instalador
makensis installer.nsi

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Instalador generado exitosamente!
    echo ========================================
    echo.
    echo Archivos generados:
    echo - Ejecutable: dist\main.exe
    echo - Instalador: dist\YouTube_MP3_Downloader_Setup.exe
    echo.
    echo NOTA: El historial de descargas se creara
    echo automaticamente en el directorio del ejecutable
    echo cuando se ejecute la aplicacion.
) else (
    echo.
    echo ========================================
    echo ERROR en la generacion del instalador
    echo ========================================
    echo.
    echo El ejecutable se ha creado exitosamente en: dist\main.exe
    echo Puedes usarlo directamente sin el instalador.
)

pause
