; NSIS Generic Installer Template v3.0
; Populated dynamically by PuffinPyEditor Installer Builder

!include "MUI2.nsh"
!include "LogicLib.nsh"

; --- Core Defines (Set by Python build script) ---
;!DEFINE_BLOCK!

; --- MUI Settings ---
!define MUI_ABORTWARNING
!define MUI_ICON "${INSTALLER_ICON}"
!define MUI_UNICON "${INSTALLER_ICON}"
!define MUI_HEADERIMAGE_BITMAP "${ASSETS_DIR}\header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "${ASSETS_DIR}\welcome.bmp"

; --- Page Order ---
!insertmacro MUI_PAGE_WELCOME
!ifdef LICENSE_FILE
    !insertmacro MUI_PAGE_LICENSE "${LICENSE_FILE}"
!endif
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "${OUT_FILE}"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
ShowInstDetails show
SetCompressor lzma

;!COMPONENT_DESCRIPTIONS!

;!INSTALL_SECTIONS!

;!UNINSTALL_SECTIONS!

Function un.onInit
    SetShellVarContext all
FunctionEnd