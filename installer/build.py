# PuffinPyEditor/installer/build.py
import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

# --- Configuration ---
APP_NAME = "PuffinPyEditor"
ROOT_DIR = Path(__file__).parent.parent
VERSION_FILE = ROOT_DIR / "VERSION.txt"
MAIN_SPEC = ROOT_DIR / "main.spec"
TRAY_SPEC = ROOT_DIR / "tray_app.spec"
LOG_VIEWER_SPEC = ROOT_DIR / "log_viewer.spec"
INSTALLER_ASSETS_SCRIPT = ROOT_DIR / "installer" / "create_installer_assets.py"
INSTALLER_SCRIPT = ROOT_DIR / "installer" / "create_installer.nsi"
DIST_DIR = ROOT_DIR / "dist"
FINAL_DIR = DIST_DIR / APP_NAME
ASSETS_DIR = ROOT_DIR / "assets"
BUILD_DIR = ROOT_DIR / "build"

# --- Colors for printing ---
class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def run_command(command, cwd=None, capture_output=False, check_for_errors=False):
    """Runs a command and exits if it fails."""
    try:
        cmd_str = ' '.join(map(str, command))
        print(f"{BColors.OKBLUE}Running: {cmd_str}{BColors.ENDC}")
        result = subprocess.run(
            command,
            check=True,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        output = (result.stdout or "") + (result.stderr or "")
        if capture_output:
            print(output)
        # Extra check for tools that don't return proper error codes
        if check_for_errors and ("error in script" in output.lower() or "aborting creation" in output.lower()):
            raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)
        return result
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"\n{BColors.FAIL}{BColors.BOLD}[FATAL ERROR] Command failed: {cmd_str}{BColors.ENDC}")
        if hasattr(e, 'stdout') and e.stdout:
            print(f"{BColors.FAIL}--- STDOUT ---\n{e.stdout}{BColors.ENDC}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"{BColors.FAIL}--- STDERR ---\n{e.stderr}{BColors.ENDC}")
        sys.exit(1)

def print_step(step_num, total_steps, message):
    """Prints a formatted step message."""
    print(f"\n{BColors.HEADER}{BColors.BOLD}===== [{step_num}/{total_steps}] {message} ====={BColors.ENDC}")

def find_nsis_path(override_path=None):
    """Finds the path to makensis.exe."""
    if override_path and Path(override_path).exists():
        print(f"  - Using NSIS path from settings: {override_path}")
        return override_path
    nsis_path = shutil.which("makensis")
    if nsis_path:
        print(f"  - Found 'makensis' on system PATH: {nsis_path}")
        return nsis_path
    if sys.platform == "win32":
        for path_str in [
            "C:\\Program Files (x86)\\NSIS\\makensis.exe",
            "C:\\Program Files\\NSIS\\makensis.exe",
        ]:
            path = Path(path_str)
            if path.exists():
                print(f"  - Found 'makensis' at default location: {path}")
                return str(path)
    return None

def main():
    parser = argparse.ArgumentParser(description=f"Build script for {APP_NAME}.")
    parser.add_argument('--cleanup', action='store_true', help="Remove temporary build directory after completion.")
    parser.add_argument('--nsis-path', type=str, help="Override path to makensis.exe.")
    parser.add_argument('--version', type=str, help="Override version from VERSION.txt.")
    args = parser.parse_args()
    print(f"{BColors.HEADER}PuffinPyEditor Build System v2.0{BColors.ENDC}")

    print_step(1, 6, "Reading Application Version")
    if args.version:
        app_version = args.version
    else:
        if not VERSION_FILE.exists():
            print(f"{BColors.FAIL}[FATAL ERROR] {VERSION_FILE} not found.{BColors.ENDC}"); sys.exit(1)
        app_version = VERSION_FILE.read_text().strip()
    print(f"  - Version identified as: {app_version}")

    step_num = 2
    for desc, spec_file in {
        "MAIN application (PuffinPyEditor.exe)": MAIN_SPEC,
        "TRAY application (PuffinPyTray.exe)": TRAY_SPEC,
        "LOG VIEWER application (log_viewer.exe)": LOG_VIEWER_SPEC,
    }.items():
        print_step(step_num, 6, f"Bundling {desc}")
        run_command([sys.executable, "-m", "PyInstaller", str(spec_file), "--noconfirm", "--distpath", str(FINAL_DIR)])
        print(f"  - {desc} bundled successfully.")
        step_num += 1

    print_step(5, 6, "Copying Application Assets")
    assets_dest = FINAL_DIR / "assets"
    if assets_dest.exists(): shutil.rmtree(assets_dest)
    shutil.copytree(ASSETS_DIR, assets_dest); print("  - Assets copied successfully.")

    print_step(6, 6, "Generating and Compiling Installer")
    print("  - Generating installer assets...")
    run_command([sys.executable, str(INSTALLER_ASSETS_SCRIPT)])
    makensis_exe = find_nsis_path(args.nsis_path)
    if not makensis_exe:
        print(f"{BColors.WARNING}[WARNING] NSIS (makensis.exe) not found. Skipping installer creation.{BColors.ENDC}")
    else:
        print(f"  - Compiling with: {makensis_exe}")
        installer_output_file = DIST_DIR / f"{APP_NAME}_v{app_version}_Setup.exe"
        nsis_cmd = [makensis_exe, f'/DAPP_VERSION={app_version}', f'/DAPP_NAME={APP_NAME}', f'/DSRC_DIR={FINAL_DIR.resolve()}', f'/DOUT_FILE={installer_output_file.resolve()}', str(INSTALLER_SCRIPT)]
        run_command(nsis_cmd, capture_output=True, check_for_errors=True)
        print(f"  - {BColors.OKGREEN}Installer created successfully at: {installer_output_file}{BColors.ENDC}")

    if args.cleanup:
        print_step("BONUS", "BONUS", "Cleaning up build artifacts")
        if BUILD_DIR.exists():
            shutil.rmtree(BUILD_DIR)
            print(f"  - Removed '{BUILD_DIR}' directory.")

    print(f"\n{BColors.OKGREEN}{BColors.BOLD}==============================================")
    print(f"    BUILD PROCESS FINISHED SUCCESSFULLY")
    print(f"=============================================={BColors.ENDC}")

if __name__ == "__main__":
    main()