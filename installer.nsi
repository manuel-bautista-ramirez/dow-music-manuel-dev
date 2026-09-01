; Script NSIS profesional para el instalador de DOW-MUSIC-MANUEL-DEV
; Instalador con características avanzadas y diseño profesional

!define APPNAME "DOW-MUSIC-MANUEL-DEV"
!define COMPANYNAME "Manuel Ramírez"
!define DESCRIPTION "Descargador de MP3 de YouTube con interfaz gráfica moderna"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/manuelramirez/youtube-mp3-downloader"
!define UPDATEURL "https://github.com/manuelramirez/youtube-mp3-downloader"
!define ABOUTURL "https://github.com/manuelramirez/youtube-mp3-downloader"
!define INSTALLSIZE 70000

RequestExecutionLevel admin

InstallDir "$PROGRAMFILES\${APPNAME}"

; Configuración de interfaz moderna
!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "WinVer.nsh"

; Configuración de MUI
!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "icon.ico"
!define MUI_HEADERIMAGE_UNBITMAP "icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "icon.ico"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "icon.ico"

; Colores personalizados
!define MUI_BGCOLOR "0xFFFFFF"
!define MUI_TEXTCOLOR "0x000000"

; Páginas del instalador
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\main.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Ejecutar YouTube MP3 Downloader"
!insertmacro MUI_PAGE_FINISH

; Páginas del desinstalador
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Idioma
!insertmacro MUI_LANGUAGE "Spanish"

; Función para verificar si la aplicación está en ejecución
Function .onInit
    ; Verificar versión de Windows (mínimo Windows 10)
    ${IfNot} ${AtLeastWin10}
        MessageBox MB_OK|MB_ICONSTOP "Este instalador requiere Windows 10 o superior."
        Quit
    ${EndIf}
    
    ; Verificar si ya está instalado
    ReadRegStr $0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString"
    ${If} $0 != ""
        MessageBox MB_YESNO|MB_ICONQUESTION "${APPNAME} ya está instalado. ¿Desea desinstalar la versión anterior?" IDYES uninst
        Abort
    ${EndIf}
    goto done
    
    uninst:
        ClearErrors
        ExecWait '$0 _?=$INSTDIR'
        IfErrors uninst_error
        goto done
        
    uninst_error:
        MessageBox MB_OK|MB_ICONSTOP "Error al desinstalar la versión anterior. Por favor, desinstálala manualmente."
        Abort
        
    done:
FunctionEnd

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
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\main.exe" "" "$INSTDIR\icon.ico" 0
    
    ; Crear acceso directo en el menú de inicio
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\main.exe" "" "$INSTDIR\icon.ico" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Desinstalar.lnk" "$INSTDIR\uninstall.exe"
    
    ; Crear acceso directo en el menú de inicio con descripción
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Sitio Web.lnk" "${HELPURL}"
    
    ; Escribir desinstalador
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Escribir claves de registro para desinstalación
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\icon.ico"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$INSTDIR\uninstall.exe /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallDate" "${__DATE__}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
    
    ; Mensaje de éxito
    DetailPrint "Instalación completada exitosamente."
SectionEnd

Section "Acceso directo en el escritorio" SecDesktop
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\main.exe" "" "$INSTDIR\icon.ico" 0
SectionEnd

Section "Licencia" SecLicense
    File "LICENSE.txt"
SectionEnd

; Descripción de las secciones
LangString DESC_SecMain ${LANG_SPANISH} "Archivos principales de la aplicación (requerido)"
LangString DESC_SecDesktop ${LANG_SPANISH} "Crear acceso directo en el escritorio"
LangString DESC_SecLicense ${LANG_SPANISH} "Archivo de licencia del proyecto"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} $(DESC_SecMain)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} $(DESC_SecDesktop)
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
    Delete "$SMPROGRAMS\${APPNAME}\Sitio Web.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"
    
    ; Borrar directorio de instalación
    RMDir $INSTDIR
    
    ; Preguntar si borrar datos de usuario
    MessageBox MB_YESNO|MB_ICONQUESTION "¿Desea eliminar también el historial de descargas y datos de usuario?" IDYES delete_data
    goto done
    
    delete_data:
        RMDir /r "$APPDATA\${APPNAME}"
    
    done:
    ; Borrar claves de registro
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    
    ; Mensaje de éxito
    MessageBox MB_OK|MB_ICONINFORMATION "${APPNAME} ha sido desinstalado exitosamente."
SectionEnd
