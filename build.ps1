# Script para compilar el proyecto en ejecutable y generar instalador
# YouTube MP3 Downloader

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Compilando YouTube MP3 Downloader..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Borrar el ejecutable anterior si existe
if (Test-Path "dist\main.exe") {
    Write-Host "Borrando ejecutable anterior..." -ForegroundColor Yellow
    Remove-Item -Path "dist\main.exe" -Force
}

# Borrar directorio build si existe
if (Test-Path "build") {
    Write-Host "Borrando directorio build anterior..." -ForegroundColor Yellow
    Remove-Item -Path "build" -Recurse -Force
}

# Borrar instalador anterior si existe
if (Test-Path "dist\YouTube_MP3_Downloader_Setup.exe") {
    Write-Host "Borrando instalador anterior..." -ForegroundColor Yellow
    Remove-Item -Path "dist\YouTube_MP3_Downloader_Setup.exe" -Force
}

# Compilar con PyInstaller
Write-Host "Iniciando compilacion con PyInstaller..." -ForegroundColor Green
& ".venv\Scripts\pyinstaller.exe" --onefile --windowed --icon=icon.ico --add-data "icon.ico;." --add-data "logo.png;." --add-data "src;src" --add-data ".venv\Lib\site-packages\ctkfontawesome\assets;ctkfontawesome\assets" --add-data ".venv\Lib\site-packages\ctkfontawesome\backends;ctkfontawesome\backends" --add-data ".venv\Lib\site-packages\ctkfontawesome\svgs;ctkfontawesome\svgs" --hidden-import ctkfontawesome --hidden-import ctkfontawesome.asset_resolver main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "ERROR en la compilacion con PyInstaller" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Read-Host "Presione Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Compilacion exitosa!" -ForegroundColor Green
Write-Host "Ejecutable creado en: dist\main.exe" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Generar instalador con NSIS
Write-Host "Generando instalador con NSIS..." -ForegroundColor Green
Write-Host ""

# Buscar makensis en ubicaciones comunes
$makensisPaths = @(
    "C:\Program Files (x86)\NSIS\Bin\makensis.exe",
    "C:\Program Files\NSIS\Bin\makensis.exe"
)

$makensisPath = $null
foreach ($path in $makensisPaths) {
    if (Test-Path $path) {
        $makensisPath = $path
        break
    }
}

if ($null -eq $makensisPath) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "ERROR: NSIS (makensis) no encontrado" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Para generar el instalador, necesitas instalar NSIS:" -ForegroundColor Yellow
    Write-Host "1. Descarga NSIS desde: https://nsis.sourceforge.io/Download" -ForegroundColor Yellow
    Write-Host "2. Instala NSIS en tu sistema" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "El ejecutable se ha creado exitosamente en: dist\main.exe" -ForegroundColor Green
    Write-Host "Puedes usarlo directamente sin el instalador." -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Red
    Read-Host "Presione Enter para salir"
    exit 1
}

# Ejecutar makensis
& $makensisPath installer.nsi

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "ERROR en la generacion del instalador" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "El ejecutable se ha creado exitosamente en: dist\main.exe" -ForegroundColor Green
    Write-Host "Puedes usarlo directamente sin el instalador." -ForegroundColor Green
} else {
    # Mover el instalador a la carpeta dist
    if (Test-Path "installer.exe") {
        Move-Item -Path "installer.exe" -Destination "dist\DOW-MUSIC-MANUEL-DEV_Setup.exe" -Force
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Instalador generado exitosamente!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Archivos generados:" -ForegroundColor Cyan
    Write-Host "- Ejecutable: dist\main.exe" -ForegroundColor Cyan
    Write-Host "- Instalador: dist\DOW-MUSIC-MANUEL-DEV_Setup.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "NOTA: El historial de descargas se creara" -ForegroundColor Yellow
    Write-Host "automaticamente en el directorio del ejecutable" -ForegroundColor Yellow
    Write-Host "cuando se ejecute la aplicacion." -ForegroundColor Yellow
}

Read-Host "Presione Enter para salir"
