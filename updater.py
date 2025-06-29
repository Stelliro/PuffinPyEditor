# PuffinPyEditor/updater.py
import sys
import os
import time
import requests
import zipfile
import shutil

# --- Configuration ---
# A set of files and folders that the updater will NEVER overwrite, even if they
# exist in the downloaded update. This protects user-specific data.
# Paths should use forward slashes and be relative to the install directory.
PROTECTED_ITEMS = {
    "puffin_editor_settings.json",
    "logs",
    "assets/themes/custom_themes.json"
}
# --- End Configuration ---


def log(message):
    """Simple logger for the updater script."""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def safe_copy(source_dir, install_dir):
    """
    Intelligently copies files from the update source to the installation
    directory, skipping any protected files or folders.
    """
    log("Starting safe copy process...")
    for root, dirs, files in os.walk(source_dir):
        # Prevent os.walk from going into protected directories
        dirs[:] = [d for d in dirs
                   if os.path.relpath(os.path.join(root, d), source_dir)
                   .replace(os.sep, '/') not in PROTECTED_ITEMS]

        # Process directories first
        for d in dirs:
            rel_path = os.path.relpath(os.path.join(root, d), source_dir)
            dest_path = os.path.join(install_dir, rel_path)
            os.makedirs(dest_path, exist_ok=True)

        # Process files
        for f in files:
            src_path = os.path.join(root, f)
            rel_path = os.path.relpath(src_path, source_dir)
            # Use forward slashes for cross-platform comparison
            if rel_path.replace(os.sep, '/') in PROTECTED_ITEMS:
                log(f"Skipping protected file: {rel_path}")
                continue
            dest_path = os.path.join(install_dir, rel_path)
            shutil.copy2(src_path, dest_path)
    log("Safe copy process finished.")


def main():
    log("PuffinPy Updater started.")

    if len(sys.argv) < 3:
        log("Error: Missing arguments. "
            "Usage: python updater.py <download_url> <install_dir>")
        return

    download_url = sys.argv[1]
    install_dir = sys.argv[2]

    log(f"Update requested for directory: {install_dir}")
    log(f"Downloading from: {download_url}")

    log("Waiting for main application to exit...")
    time.sleep(2)

    try:
        log("Downloading new version...")
        response = requests.get(download_url, stream=True)
        response.raise_for_status()

        zip_path = os.path.join(install_dir, "update.zip")
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        log("Download complete.")

    except requests.exceptions.RequestException as e:
        log(f"Error: Failed to download update. {e}")
        return

    backup_dir = os.path.join(install_dir,
                              f"PuffinPyEditor_backup_{int(time.time())}")
    log(f"Creating backup at: {backup_dir}")
    try:
        # Update ignore pattern to also ignore temp update files
        ignore_patterns = shutil.ignore_patterns(
            'PuffinPyEditor_backup_*', 'update_temp', '*.zip', '*.log',
            'venv', '.git*'
        )
        shutil.copytree(install_dir, backup_dir, ignore=ignore_patterns)
    except Exception as e:
        log(f"Warning: Could not create full backup. {e}")

    temp_extract_dir = os.path.join(install_dir, "update_temp")
    try:
        log("Unzipping update...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_dir)

        # Check if the zip contains a single root folder
        extracted_content = os.listdir(temp_extract_dir)
        source_dir = temp_extract_dir
        if len(extracted_content) == 1:
            possible_root = os.path.join(temp_extract_dir, extracted_content[0])
            if os.path.isdir(possible_root):
                log(f"Update is in a root folder: {extracted_content[0]}")
                source_dir = possible_root

        log(f"Replacing files in '{install_dir}' using safe copy method.")
        safe_copy(source_dir, install_dir)
        log("Update successfully installed.")

    except Exception as e:
        log(f"Error: Failed during installation. {e}")
        log("Attempting to restore from backup...")
        # (Restore logic would go here if implemented)
        return

    finally:
        log("Cleaning up temporary files...")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir)

    log("Update process finished. Relaunch application to see the changes.")


if __name__ == "__main__":
    main()