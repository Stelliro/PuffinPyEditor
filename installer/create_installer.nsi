; PuffinPyEditor NSIS Installer Script
; Version 3.1 - Corrected File Paths

; Use variables passed from the command line by build.py
!ifndef APP_NAME
  !error "APP_NAME must be defined on the command line!"
!endif
!ifndef APP_VERSION
  !error "APP_VERSION must be defined on the command line!"
!endif
!ifndef SRC_DIR
  !error "SRC_DIR must be defined on the command line!"
!endif
!ifndef OUT_FILE
  !error "OUT_FILE must be defined on the command line!"
!endif

;--------------------------------
; Includes
!include "MUI2.nsh"
!include "FileFunc.nsh"

;--------------------------------
; General
Name "${APP_NAME}"
OutFile "${OUT_FILE}"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
InstallDirRegKey HKLM "Software\${APP_NAME}" "Install_Dir"
RequestExecutionLevel admin
SetCompressor lzma

;--------------------------------
; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "assets\PuffinPyEditor.ico"
!define MUI_UNICON "assets\PuffinPyEditor.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "assets\PuffinPyEditor_Header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "assets\welcome.bmp"

;--------------------------------
; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE.md"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
; Languages
!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Installer Sections

Section "PuffinPyEditor Core" SecPuffinPy
  SectionIn RO ; Read-only, this section is required
  SetOutPath $INSTDIR

  ; Core executables and libraries
  File "${SRC_DIR}\*.exe"
  ; REMOVED: These lines are incorrect. PyInstaller places DLLs/PYDs in subdirectories,
  ; which are already handled by the recursive File commands below.
  ; File "${SRC_DIR}\*.dll"
  ; File "${SRC_DIR}\*.pyd"
  File "${SRC_DIR}\base_library.zip"
  
  ; Required directories
  File /r "${SRC_DIR}\app_core"
  File /r "${SRC_DIR}\plugins"
  File /r "${SRC_DIR}\ui"
  File /r "${SRC_DIR}\utils"
  
  ; Required assets
  File /r "${SRC_DIR}\assets\fonts"
  SetOutPath "$INSTDIR\assets\themes"
  File "${SRC_DIR}\assets\themes\icon_colors.json"
  
  SetOutPath $INSTDIR
  ; Root files
  File "${SRC_DIR}\LICENSE.md"
  File "${SRC_DIR}\README.md"
  File "${SRC_DIR}\VERSION.txt"
  
  ; Write registry keys for Add/Remove Programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\${APP_NAME}" "Install_Dir" "$INSTDIR"

  ; Write the uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; Create Start Menu shortcuts
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\PuffinPyEditor.exe"
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\PuffinPyEditor.exe"
SectionEnd

Section "Core Debug Tools" SecDebugTools
  SetOutPath $INSTDIR
  File /r "${SRC_DIR}\core_debug_tools"
SectionEnd

Section "AI Prompt Templates" SecAIPrompts
  SetOutPath "$INSTDIR\assets"
  File /r "${SRC_DIR}\assets\prompts"
SectionEnd

Section "Additional Custom Themes" SecCustomThemes
  SetOutPath "$INSTDIR\assets\themes"
  File "${SRC_DIR}\assets\themes\custom_themes.json"
SectionEnd

; Section descriptions for the components page
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecPuffinPy} "The core application files. Required for the editor to run."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDebugTools} "Developer tools for debugging the editor and its plugins."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecAIPrompts} "A collection of prompt templates for various AI-assisted tasks."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecCustomThemes} "A set of extra visual themes created by the community."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
; Uninstaller Section
Section "Uninstall"
  ; Remove all files and directories
  Delete "$INSTDIR\*.*"
  RmDir /r "$INSTDIR\app_core"
  RmDir /r "$INSTDIR\plugins"
  RmDir /r "$INSTDIR\ui"
  RmDir /r "$INSTDIR\utils"
  RmDir /r "$INSTDIR\assets"
  RmDir /r "$INSTDIR\core_debug_tools"

  ; Remove shortcuts
  Delete "$SMPROGRAMS\${APP_NAME}\*.*"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  RmDir /r "$SMPROGRAMS\${APP_NAME}"
  
  ; Remove main install directory if empty
  RmDir "$INSTDIR"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
  DeleteRegKey HKLM "Software\${APP_NAME}"
SectionEnd