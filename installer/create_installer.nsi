; PuffinPyEditor NSIS Installer Script
; Version 4 - Corrected InstallDirRegKey command

;--------------------------------
; Includes
!include "MUI2.nsh"
!include "FileFunc.nsh"

;--------------------------------
; Defines
!define APP_NAME "PuffinPyEditor"
!define EXE_NAME "PuffinPyEditor.exe"
!define TRAY_EXE_NAME "PuffinPyTray.exe"
!define TRAY_LNK_NAME "PuffinPyEditor Tray.lnk"
!define COMPANY_NAME "PuffinPyEditorProject"
!define REG_KEY "Software\${COMPANY_NAME}\${APP_NAME}"
!define LICENSE_FILE "..\LICENSE.md"

; The version is passed from build.bat via /DVERSION=x.x.x
!ifndef VERSION
  !define VERSION "1.0.0" ; Fallback version
!endif

;--------------------------------
; MUI Settings
!define MUI_ICON "assets\PuffinPyEditor.ico"
!define MUI_UNICON "assets\PuffinPyEditor.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "assets\welcome.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "assets\PuffinPyEditor_Header.bmp"
!define MUI_ABORTWARNING

;--------------------------------
; Installer Attributes
Name "${APP_NAME} ${VERSION}"
OutFile "..\dist\${APP_NAME}_v${VERSION}_Setup.exe"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
InstallDirRegKey HKCU "${REG_KEY}" "" ; <-- CORRECTED COMMAND
RequestExecutionLevel admin

;--------------------------------
; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${LICENSE_FILE}"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
; Language
!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Section Descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_CORE} "Installs the core application files."
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_STARTMENU} "Creates a shortcut in the Start Menu."
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_DESKTOP} "Creates a shortcut on the Desktop."
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_TRAY} "Configures the tray application to launch when you log in to Windows."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
; --- Sections ---
Section "PuffinPyEditor (required)" SEC_CORE
    SectionIn RO
    SetOutPath "$INSTDIR"
    File /r "..\dist\${APP_NAME}\*"

    WriteRegStr HKCU "${REG_KEY}" "" "$INSTDIR"
    WriteUninstaller "$INSTDIR\uninstall.exe"

    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" '"$INSTDIR\${EXE_NAME}"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${COMPANY_NAME}"
SectionEnd

Section "Start Menu Shortcut" SEC_STARTMENU
    !define StartMenuFolder "${APP_NAME}"
    WriteRegStr HKCU "${REG_KEY}" "StartMenuFolder" "${StartMenuFolder}"

    CreateDirectory "$SMPROGRAMS\${StartMenuFolder}"
    CreateShortcut "$SMPROGRAMS\${StartMenuFolder}\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
    CreateShortcut "$SMPROGRAMS\${StartMenuFolder}\Uninstall ${APP_NAME}.lnk" "$INSTDIR\uninstall.exe"
SectionEnd

Section "Desktop Shortcut" SEC_DESKTOP
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
SectionEnd

Section "Launch at Startup (via Tray App)" SEC_TRAY
    CreateShortcut "$STARTUP\${TRAY_LNK_NAME}" "$INSTDIR\${TRAY_EXE_NAME}"
SectionEnd

; --- Uninstaller Section ---
Section "Uninstall"
    RMDir /r "$INSTDIR"
    
    ReadRegStr $R0 HKCU "${REG_KEY}" "StartMenuFolder"
    StrCmp $R0 "" skip_startmenu_remove
        Delete "$SMPROGRAMS\$R0\${APP_NAME}.lnk"
        Delete "$SMPROGRAMS\$R0\Uninstall ${APP_NAME}.lnk"
        RMDir "$SMPROGRAMS\$R0"
    skip_startmenu_remove:

    Delete "$DESKTOP\${APP_NAME}.lnk"
    Delete "$STARTUP\${TRAY_LNK_NAME}"
    
    DeleteRegKey HKCU "${REG_KEY}"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
SectionEnd