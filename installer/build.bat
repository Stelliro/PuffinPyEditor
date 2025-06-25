@echo off
setlocal enabledelayedexpansion

echo.
echo  ================================================
echo     PuffinPyEditor Build Script (v12 - Assets Fix)
echo  ================================================
echo.

REM --- Default Configuration ---
set "APP_NAME=PuffinPyEditor"
set "MAIN_SPEC=main.spec"
set "TRAY_SPEC=tray_app.spec"
set "LOG_VIEWER_SPEC=log_viewer.spec"
set "FINAL_DIR=dist\!APP_NAME!"
set "FINAL_EXE=!FINAL_DIR!\!APP_NAME!.exe"
set "VERSION_FILE=VERSION.txt"
set "INSTALLER_SCRIPT=installer\create_installer.nsi"
set "CLEANUP=false"
set "NSIS_PATH_OVERRIDE="
set "VERSION_OVERRIDE="

REM --- Argument Parsing ---
:arg_loop
if "%~1"=="" goto :arg_loop_end
if /I "%~1"=="cleanup" (
    set "CLEANUP=true"
    shift
    goto :arg_loop
)
if /I "%~1"=="--nsis-path" (
    set "NSIS_PATH_OVERRIDE=%~2"
    shift
    shift
    goto :arg_loop
)
if /I "%~1"=="--version" (
    set "VERSION_OVERRIDE=%~2"
    shift
    shift
    goto :arg_loop
)
shift
goto :arg_loop
:arg_loop_end

REM --- Step 1: Read Version ---
if defined VERSION_OVERRIDE (
    set "APP_VERSION=!VERSION_OVERRIDE!"
    echo [1/6] Using version from command line: !APP_VERSION!
) else (
    echo [1/6] Reading application version from file...
    if not exist "!VERSION_FILE!" (
        echo [FATAL ERROR] !VERSION_FILE! not found.
        exit /b 1
    )
    set /p APP_VERSION=<!VERSION_FILE!
    echo   - Version identified as: !APP_VERSION!
)
echo.

REM --- Step 2: Bundle Main Application (Optimized & Robust) ---
if exist "!FINAL_EXE!" goto :skip_main_bundle

echo [2/6] Bundling MAIN application (PuffinPyEditor.exe)...
call pyinstaller !MAIN_SPEC! --noconfirm
if errorlevel 1 exit /b 1
echo   - Main application bundled successfully.
goto :after_main_bundle

:skip_main_bundle
echo [2/6] Skipping MAIN application bundle (already exists).

:after_main_bundle
echo.


REM --- Step 3: Bundle Tray Application ---
echo [3/6] Bundling TRAY application (PuffinPyTray.exe)...
call pyinstaller !TRAY_SPEC! --noconfirm --distpath "!FINAL_DIR!"
if errorlevel 1 exit /b 1
echo   - Tray application bundled successfully.
echo.

REM --- Step 4: Bundle Log Viewer ---
echo [4/6] Bundling LOG VIEWER application (log_viewer.exe)...
call pyinstaller !LOG_VIEWER_SPEC! --noconfirm --distpath "!FINAL_DIR!"
if errorlevel 1 exit /b 1
echo   - Log viewer bundled successfully.
echo.

REM --- Step 5: Copy Assets ---
echo [5/6] Copying application assets...
xcopy "assets" "!FINAL_DIR!\assets\" /E /I /Y /Q
if errorlevel 1 (
    echo [FATAL ERROR] Failed to copy assets folder.
    exit /b 1
)
echo   - Assets copied successfully.
echo.

REM --- Step 6: Create Installer ---
echo [6/6] Generating assets and compiling installer...
call python "installer\create_icon.py"
if errorlevel 1 exit /b 1

call python "installer\create_welcome_image.py"
if errorlevel 1 exit /b 1

call python "installer\create_header_image.py"
if errorlevel 1 exit /b 1
echo   - Installer assets generated.

set "MAKENSIS_CMD="
if defined NSIS_PATH_OVERRIDE (
    set "MAKENSIS_CMD=!NSIS_PATH_OVERRIDE!"
    echo   - Using NSIS path from settings.
)

if not defined MAKENSIS_CMD (
    where /q makensis
    if not errorlevel 1 (
        set "MAKENSIS_CMD=makensis"
    )
)

if not defined MAKENSIS_CMD (
    echo [WARNING] NSIS ^(makensis.exe^) not found on PATH or in settings. Skipping installer creation.
    goto :cleanup
)

echo   - NSIS found. Compiling with: "!MAKENSIS_CMD!"
call "!MAKENSIS_CMD!" "/DVERSION=!APP_VERSION!" "!INSTALLER_SCRIPT!"
if errorlevel 1 exit /b 1

echo   - Installer created successfully in the 'dist' folder!
echo.

:cleanup
if /I "!CLEANUP!"=="true" (
    echo.
    echo [BONUS] Cleaning up temporary build directory...
    if exist "build" (
        rd /s /q "build"
        echo   - Successfully removed 'build' directory.
    )
)

echo.
echo  ==============================================
echo      BUILD PROCESS FINISHED SUCCESSFULLY
echo  ==============================================

exit /b 0