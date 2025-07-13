# /app_core/golden_rules.py
import os
import json
import shutil
import re
from utils.helpers import get_base_path
from utils.logger import log

ASSETS_PATH = os.path.join(get_base_path(), "assets")
GOLDEN_RULES_PATH = os.path.join(ASSETS_PATH, "golden_rules.json")
DEFAULT_RULES_PATH = os.path.join(ASSETS_PATH, "golden_presets", "default_puffinpy_rules.json")

def _initialize_rules():
    """Ensure golden_rules.json exists, creating it from default if not."""
    if not os.path.exists(GOLDEN_RULES_PATH):
        try:
            os.makedirs(os.path.dirname(GOLDEN_RULES_PATH), exist_ok=True)
            if not os.path.exists(DEFAULT_RULES_PATH):
                log.error(f"Default golden rules preset not found at {DEFAULT_RULES_PATH}. Cannot initialize golden rules.")
                # Create an empty file to prevent repeated attempts
                with open(GOLDEN_RULES_PATH, 'w', encoding='utf-8') as f:
                    json.dump({"name": "Empty Rules", "description": "Default preset not found.", "rules": []}, f, indent=4)
                return
            shutil.copy(DEFAULT_RULES_PATH, GOLDEN_RULES_PATH)
            log.info(f"Initialized golden rules at {GOLDEN_RULES_PATH}")
        except Exception as e:
            log.error(f"Could not create initial golden rules: {e}")

def get_golden_rules() -> list[str]:
    """
    Returns a list of fundamental, non-negotiable rules for the AI.
    These rules are loaded from the editable golden_rules.json.
    """
    _initialize_rules()
    try:
        with open(GOLDEN_RULES_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("rules", [])
    except (IOError, json.JSONDecodeError) as e:
        log.error(f"Failed to load golden rules from {GOLDEN_RULES_PATH}: {e}. Returning empty list.")
        return []

def get_golden_rules_text() -> str:
    """Returns the golden rules as a numbered text block for editing."""
    rules = get_golden_rules()
    if not rules:
        return ""
    return "\n".join(f"{i+1}. {rule}" for i, rule in enumerate(rules))

def save_golden_rules_from_text(text: str) -> bool:
    """
    Parses a numbered or un-numbered text block and saves the rules. [2, 3]
    """
    rules = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        # Regex to strip optional leading numbers and punctuation
        match = re.match(r'^\s*\d+\s*[.\-:]?\s*(.*)', line)
        if match:
            cleaned_line = match.group(1).strip()
        else:
            cleaned_line = line
        if cleaned_line:
            rules.append(cleaned_line)

    _initialize_rules() # Ensure file exists before reading
    try:
        with open(GOLDEN_RULES_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (IOError, json.JSONDecodeError):
        data = {}
        
    data["rules"] = rules
    data.setdefault("name", "Custom Golden Rules")
    data.setdefault("description", "User-defined golden rules for AI interaction.")

    try:
        with open(GOLDEN_RULES_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        log.info("Golden rules saved successfully.")
        return True
    except IOError as e:
        log.error(f"Failed to save golden rules: {e}")
        return False

def reset_golden_rules_to_default() -> bool:
    """Resets the user's golden rules to the default preset."""
    try:
        if not os.path.exists(DEFAULT_RULES_PATH):
            log.error(f"Default rules file not found at {DEFAULT_RULES_PATH}. Cannot reset.")
            return False
        shutil.copy(DEFAULT_RULES_PATH, GOLDEN_RULES_PATH)
        log.info(f"Reset golden rules at {GOLDEN_RULES_PATH} to default.")
        return True
    except Exception as e:
        log.error(f"Could not reset golden rules: {e}")
        return False