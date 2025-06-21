# PuffinPyEditor/utils/validate_assets.py
import os

script_content = """
import os
import json
import re
import jsonschema
from typing import List, Dict, Any, Tuple

# --- Configuration ---
# Adjust these paths if your project structure changes
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEMES_DIR = os.path.join(ROOT_DIR, "assets", "themes")
BUILT_IN_THEMES_FILE = os.path.join(THEMES_DIR, "themes.json")
CUSTOM_THEMES_FILE = os.path.join(THEMES_DIR, "custom_themes.json")
THEME_SCHEMA_FILE = os.path.join(THEMES_DIR, "theme_schema.json")
THEME_MANAGER_FILE = os.path.join(ROOT_DIR, "app_core", "theme_manager.py")

class bcolors:
    HEADER = '\\033[95m'
    OKBLUE = '\\033[94m'
    OKGREEN = '\\033[92m'
    WARNING = '\\033[93m'
    FAIL = '\\033[91m'
    ENDC = '\\033[0m'
    BOLD = '\\033[1m'

def _print_header(title: str):
    print(f"\\n{bcolors.HEADER}{bcolors.BOLD}===== {title.upper()} ====={bcolors.ENDC}")

def _load_json_file(filepath: str) -> Tuple[Any, List[str]]:
    \"\"\"Loads a JSON file and returns its content and any errors found.\"\"\"
    errors = []
    data = None
    if not os.path.exists(filepath):
        # This is not an error, the file might be optional (like custom_themes)
        return None, errors

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON syntax in '{os.path.basename(filepath)}':\\n  {bcolors.FAIL}L{e.lineno}:C{e.colno} - {e.msg}{bcolors.ENDC}")
    except Exception as e:
        errors.append(f"Could not read '{os.path.basename(filepath)}': {e}")

    return data, errors

def validate_json_syntax() -> Tuple[Dict, List[str]]:
    \"\"\"Checks basic JSON syntax of theme files.\"\"\"
    _print_header("1. JSON Syntax Validation")

    all_themes = {}
    all_errors = []

    # Validate built-in themes
    built_in_data, errors = _load_json_file(BUILT_IN_THEMES_FILE)
    all_errors.extend(errors)
    if built_in_data:
        all_themes.update(built_in_data)

    # Validate custom themes (if they exist)
    custom_data, errors = _load_json_file(CUSTOM_THEMES_FILE)
    all_errors.extend(errors)
    if custom_data:
        all_themes.update(custom_data)

    if not all_errors:
        print(f"{bcolors.OKGREEN}All theme files are valid JSON.{bcolors.ENDC}")

    return all_themes, all_errors

def validate_theme_schemas(all_themes: Dict, schema_file: str) -> List[str]:
    \"\"\"Validates each theme against the defined JSON schema.\"\"\"
    _print_header("2. Theme Schema Validation")

    schema, errors = _load_json_file(schema_file)
    if errors:
        return errors

    all_errors = []

    for theme_id, theme_data in all_themes.items():
        try:
            jsonschema.validate(instance=theme_data, schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            # Provide a more user-friendly error message
            error_path = " -> ".join(map(str, e.path))
            errors.append(
                f"Theme '{bcolors.BOLD}{theme_id}{bcolors.ENDC}' failed schema validation at '{bcolors.WARNING}{error_path}{bcolors.ENDC}':\\n  {bcolors.FAIL}{e.message}{bcolors.ENDC}"
            )

    if not all_errors:
        print(f"{bcolors.OKGREEN}All themes conform to the required schema.{bcolors.ENDC}")

    return all_errors

def get_required_color_keys_from_code(manager_file: str) -> set:
    \"\"\"Extracts color keys like 'window.background' from the QSS in theme_manager.py.\"\"\"
    required_keys = set()
    if not os.path.exists(manager_file):
        return required_keys

    with open(manager_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find all instances of c("some.key", ...)
    matches = re.findall(r'c\\("([^"]+)"', content)
    for key in matches:
        required_keys.add(key)

    return required_keys

def validate_key_completeness(all_themes: Dict, required_keys: set) -> List[str]:
    \"\"\"Checks if each theme defines all the keys required by the application code.\"\"\"
    _print_header("3. Color Key Completeness Validation")
    all_errors = []

    if not required_keys:
        all_errors.append(f"{bcolors.FAIL}Could not find any required color keys in ThemeManager. Check path.{bcolors.ENDC}")
        return all_errors

    print(f"Found {len(required_keys)} required color keys in the application code.")

    for theme_id, theme_data in all_themes.items():
        theme_keys = set(theme_data.get("colors", {}).keys())
        missing_keys = required_keys - theme_keys

        if missing_keys:
            all_errors.append(
                f"Theme '{bcolors.BOLD}{theme_id}{bcolors.ENDC}' is missing {len(missing_keys)} required color keys:"
            )
            for key in sorted(list(missing_keys)):
                 all_errors.append(f"  - {bcolors.WARNING}{key}{bcolors.ENDC}")

    if not all_errors:
        print(f"{bcolors.OKGREEN}All themes have the required color keys.{bcolors.ENDC}")

    return all_errors

def main():
    \"\"\"Run all validation checks.\"\"\"
    print(f"{bcolors.BOLD}Running PuffinPyEditor Asset Validator...{bcolors.ENDC}")

    # 1. Syntax Check
    all_themes, errors = validate_json_syntax()
    if errors:
        for error in errors:
            print(f"- {error}")
        print(f"\\n{bcolors.FAIL}{bcolors.BOLD}Validation failed at Step 1. Cannot continue.{bcolors.ENDC}")
        return

    # 2. Schema Check
    errors = validate_theme_schemas(all_themes, THEME_SCHEMA_FILE)
    if errors:
        for error in errors:
            print(f"- {error}")

    # 3. Completeness Check
    required_keys = get_required_color_keys_from_code(THEME_MANAGER_FILE)
    errors.extend(validate_key_completeness(all_themes, required_keys))

    _print_header("Validation Summary")
    if errors:
        print(f"{bcolors.FAIL}{bcolors.BOLD}Validation finished with {len(errors)} issue(s). See details above.{bcolors.ENDC}")
    else:
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}All assets validated successfully!{bcolors.ENDC}")

if __name__ == "__main__":
    main()

"""

file_path = "MACK PUFFINPYEDITOR/utils/validate_assets.py"
try:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    print(f"Created validation script at {file_path}")
except Exception as e:
    print(f"Failed to create validation script: {e}")