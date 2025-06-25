; PuffinPyEditor NSIS Installer Script
; Version 3 - Corrected file path and startup link warnings

;--------------------------------
; Includes
!include MUI2.nsh
!include FileFunc.nsh

;--------------------------------
; Defines
!define APP_NAME "PuffinPyEditor"
!define EXE_NAME "PuffinPyEditor.exe"
!define TRAY_EXE_NAME "PuffinPyTray.exe"
!define TRAY_LNK_NAME "PuffinPyEditor Tray.lnk"
!define COMPANY_NAME "PuffinPyEditorProject"
!define REG_KEY "Software\PuffinPyEditorProject\PuffinPyEditor"

; Version is passed from the build script with /DVERSION=x.x.x
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
InstallDirRegKey HKCU "${REG_KEY}" ""
RequestExecutionLevel admin

;--------------------------------
; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE.md"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
Var StartMenuFolder
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
; Language
!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Sections

Section "PuffinPyEditor (required)" SEC_CORE
  SectionIn RO
  SetOutPath "$INSTDIR"
  
  ; Correctly navigate to the bundled application directory
  File /r "..\dist\${APP_NAME}\*.*"

  ; Create uninstaller
  WriteRegStr HKCU "${REG_KEY}" "" "$INSTDIR"
  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; Add to Add/Remove Programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\${EXE_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${COMPANY_NAME}"
SectionEnd

Section "Start Menu Shortcut" SEC_STARTMENU
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Uninstall ${APP_NAME}.lnk" "$INSTDIR\uninstall.exe"
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section "Desktop Shortcut" SEC_DESKTOP
  CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
SectionEnd

Section "Launch at Startup (via Tray App)" SEC_TRAY
  ; --- FIX for warning 6000 ---
  ; Construct the full path in a variable ($0) first.
  StrCpy $0 "$STARTUP\${TRAY_LNK_NAME}"
  CreateShortcut "$0" "$INSTDIR\${TRAY_EXE_NAME}"
SectionEnd

; --- Descriptions for Components Page ---
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_CORE} "Installs the core application files."
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_STARTMENU} "Creates a shortcut in the Start Menu."
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_DESKTOP} "Creates a shortcut on the Desktop."
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_TRAY} "Automatically starts the background tray application on Windows login."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
; Uninstaller Section
Section "Uninstall"
  Delete "$INSTDIR\uninstall.exe"
  RMDir /r "$INSTDIR"

  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
  Delete "$SMPROGRAMS\$StartMenuFolder\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall ${APP_NAME}.lnk"
  RMDir "$SMPROGRAMS\$StartMenuFolder"

  Delete "$DESKTOP\${APP_NAME}.lnk"
  
  ; --- FIX for warning 6000 ---
  ; Construct the full path in a variable ($0) first.
  StrCpy $0 "$STARTUP\${TRAY_LNK_NAME}"
  Delete "$0"

  DeleteRegKey HKCU "${REG_KEY}"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
SectionEnd