; Script NSIS para el instalador de YouTube MP3 Downloader
; Genera un instalador profesional con desinstalador

!define APPNAME "YouTube MP3 Downloader"
!define COMPANYNAME "Manuel Ramírez"
!define DESCRIPTION "Descargador de MP3 de YouTube con interfaz gráfica moderna"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/manuelramirez/youtube-mp3-downloader" ; URL de soporte
!define UPDATEURL "https://github.com/manuelramirez/youtube-mp3-downloader" ; URL de actualizaciones
!define ABOUTURL "https://github.com/manuelramirez/youtube-mp3-downloader" ; URL "Acerca de"
!define INSTALLSIZE 70000 ; Tamaño estimado en KB (aprox 70 MB)

RequestExecutionLevel admin ; Requiere permisos de administrador

InstallDir "$PROGRAMFILES\${APPNAME}"

; Interfaz moderna
!include "MUI2.nsh"

; Páginas del instalador
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Páginas del desinstalador
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Idioma
!insertmacro MUI_LANGUAGE "Spanish"

; Secciones
Section "Archivos principales" SecMain
    SectionIn RO
    
    SetOutPath $INSTDIR
    File "dist\main.exe"
    File "icon.ico"
    File "logo.png"
    
    ; Crear directorio para historial de descargas
    CreateDirectory "$APPDATA\${APPNAME}"
    
    ; Crear acceso directo en el escritorio
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\main.exe" "" "$INSTDIR\icon.ico"
    
    ; Crear acceso directo en el menú de inicio
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\main.exe" "" "$INSTDIR\icon.ico"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Desinstalar.lnk" "$INSTDIR\uninstall.exe"
    
    ; Escribir desinstalador
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Escribir claves de registro para desinstalación
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$INSTDIR\uninstall.exe /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$INSTDIR"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
SectionEnd

Section "Licencia" SecLicense
    File "LICENSE.txt"
SectionEnd

; Descripción de las secciones
LangString DESC_SecMain ${LANG_SPANISH} "Archivos principales de la aplicación"
LangString DESC_SecLicense ${LANG_SPANISH} "Archivo de licencia del proyecto"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} $(DESC_SecMain)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecLicense} $(DESC_SecLicense)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Sección de desinstalación
Section "Uninstall"
    ; Borrar archivos
    Delete $INSTDIR\main.exe
    Delete $INSTDIR\icon.ico
    Delete $INSTDIR\logo.png
    Delete $INSTDIR\LICENSE.txt
    Delete $INSTDIR\uninstall.exe
    
    ; Borrar accesos directos
    Delete "$DESKTOP\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\Desinstalar.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"
    
    ; Borrar directorio de instalación
    RMDir $INSTDIR
    
    ; Borrar directorio de datos de aplicación
    RMDir /r "$APPDATA\${APPNAME}"
    
    ; Borrar claves de registro
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd
