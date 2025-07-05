; PuffinPyEditor NSIS Installer Script
; ===================================
; Version 1.6 - With Modern UI & Corrected Section Defines

!include "MUI2.nsh"
!include "FileFunc.nsh"

; --- Application & System Info ---
!define APP_NAME "PuffinPyEditor"
!define EXE_NAME "PuffinPyEditor.exe"
!define TRAY_EXE_NAME "PuffinPyTray.exe"
!define TRAY_LNK_NAME "PuffinPyEditor Tray.lnk"
!define COMPANY_NAME "PuffinPyEditorProject"
!define REG_KEY "Software\${COMPANY_NAME}\${APP_NAME}"
!define LICENSE_FILE "..\LICENSE.md"

; --- Section Identifiers (using unique strings) ---
!define SEC_CORE "CoreFiles"
!define SEC_STARTMENU "StartMenuShortcut"
!define SEC_DESKTOP "DesktopShortcut"
!define SEC_TRAY "StartupTray"

; --- Modern UI Configuration ---
!define MUI_ICON "assets\PuffinPyEditor.ico"
!define MUI_UNICON "assets\PuffinPyEditor.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "assets\welcome.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "assets\PuffinPyEditor_Header.bmp"
!define MUI_ABORTWARNING

; --- Pages ---
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${LICENSE_FILE}"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; --- Language ---
!insertmacro MUI_LANGUAGE "English"

; --- Descriptions for Components Page ---
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_CORE} "Installs the main application files."
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_STARTMENU} "Creates a shortcut in the Start Menu."
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_DESKTOP} "Creates a shortcut on the Desktop."
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_TRAY} "Installs the background tray application for quick launching."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; ===================================================================
;   INSTALLATION SECTION
; ===================================================================

Section "PuffinPyEditor (required)" ${SEC_CORE}
    SectionIn RO ; Read-only, user can't uncheck
    SetOutPath $INSTDIR
    File /r "..\dist\PuffinPyEditor\*"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Write registry keys for Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" '"$INSTDIR\${EXE_NAME}"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${COMPANY_NAME}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
SectionEnd

Section "Start Menu Shortcut" ${SEC_STARTMENU}
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\Uninstall ${APP_NAME}.lnk" "$INSTDIR\uninstall.exe"
SectionEnd

Section "Desktop Shortcut" ${SEC_DESKTOP}
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
SectionEnd

Section "Launch on Startup (Tray App)" ${SEC_TRAY}
    CreateShortCut "$STARTUP\${TRAY_LNK_NAME}" "$INSTDIR\${TRAY_EXE_NAME}"
SectionEnd

; ===================================================================
;   UNINSTALLATION SECTION
; ===================================================================

Section "Uninstall"
    ; Remove files
    Delete "$INSTDIR\*.*"
    RMDir /r "$INSTDIR\assets"
    RMDir /r "$INSTDIR\plugins"
    RMDir /r "$INSTDIR\core_debug_tools"
    RMDir /r "$INSTDIR\ui"
    RMDir /r "$INSTDIR\utils"
    RMDir /r "$INSTDIR\app_core"

    ; Remove shortcuts
    Delete "$SMPROGRAMS\${APP_NAME}\*.*"
    RMDir "$SMPROGRAMS\${APP_NAME}"
    Delete "$DESKTOP\${APP_NAME}.lnk"
    Delete "$STARTUP\${TRAY_LNK_NAME}"
    
    ; Remove directory
    RMDir $INSTDIR
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    DeleteRegKey HKCU "${REG_KEY}"
SectionEnd