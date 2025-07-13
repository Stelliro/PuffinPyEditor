; NSIS Generic Installer Template v2.0
; This script is populated dynamically by the PuffinPyEditor Installer Builder plugin.

;================================
;==         DEFINES            ==
; These are set by the build script via the /D flag
;================================
!define PRODUCT_NAME "${APP_NAME}"
!define PRODUCT_VERSION "${APP_VERSION}"
!define PRODUCT_AUTHOR "${APP_AUTHOR}"
!define MAIN_EXE "${MAIN_EXE}"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

;================================
;==       MUI SETTINGS         ==
;================================
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "${ASSETS_DIR}\installer_icon.ico"
!define MUI_UNICON "${ASSETS_DIR}\installer_icon.ico"
!define MUI_HEADERIMAGE_BITMAP "${ASSETS_DIR}\header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "${ASSETS_DIR}\welcome.bmp"

;================================
;==        PAGE SETUP          ==
;================================
!insertmacro MUI_PAGE_WELCOME
!ifdef LICENSE_PATH
    !insertmacro MUI_PAGE_LICENSE "${LICENSE_PATH}"
!endif
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "${OUT_FILE}"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
ShowInstDetails show
SetCompressor lzma

; --- DYNAMIC CONTENT INJECTED BY BUILD SCRIPT ---

; !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
;   !insertmacro MUI_DESCRIPTION_TEXT ${SEC_01} "Description for Main Section."
;   !insertmacro MUI_DESCRIPTION_TEXT ${SEC_02} "Description for Shortcuts."
; !insertmacro MUI_FUNCTION_DESCRIPTION_END

;!GENERATED_SECTIONS_GO_HERE!

Function un.onInit
    SetShellVarContext all
FunctionEnd