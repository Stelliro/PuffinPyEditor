# /plugins/ai_patcher/response_parser.py
import os
import re
from typing import Dict, Tuple
from utils.logger import log

def parse_llm_response(response_text: str) -> Dict[str, str]:
    """
    Parses a markdown response from an LLM to extract file paths and their content.
    Expected format:
    ### File: /path/to/your/file.py
    ```python
    # new file content
    ```
    """
    changes = {}
    # This regex looks for '### File: /path/to/file.ext' and captures the path.
    # It also handles optional backticks around the path.
    # Then it non-greedily captures everything until the final '```'.
    # `re.DOTALL` allows `.` to match newlines.
    pattern = re.compile(
        r"###\s+File:\s+`?(/.*?)`?\s*\n```[a-zA-Z]*\n(.*?)\n```",
        re.DOTALL
    )

    for match in pattern.finditer(response_text):
        filepath = match.group(1).strip()
        content = match.group(2)
        changes[filepath] = content
        log.info(f"AI Patcher: Parsed update for file '{filepath}'.")

    return changes

def apply_changes_to_project(project_root: str, changes: Dict[str, str]) -> Tuple[bool, str]:
    """
    Applies the parsed changes to the files in the project directory.

    Args:
        project_root: The absolute path to the root of the project.
        changes: A dictionary mapping relative file paths to their new content.

    Returns:
        A tuple (success, message).
    """
    if not project_root or not os.path.isdir(project_root):
        return False, "Invalid project root directory."

    if not changes:
        return False, "No file changes were found in the provided text."

    errors = []
    success_count = 0

    for rel_path, content in changes.items():
        # Sanitize the relative path, removing any leading slashes
        clean_rel_path = rel_path.lstrip('/').lstrip('\\')
        abs_path = os.path.join(project_root, clean_rel_path)

        # Security check: ensure the final path is within the project root
        if not os.path.abspath(abs_path).startswith(os.path.abspath(project_root)):
            msg = f"Skipped unsafe path: '{rel_path}' resolves outside the project directory."
            log.error(f"AI Patcher: {msg}")
            errors.append(msg)
            continue

        try:
            # Ensure the directory for the file exists
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)

            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(content)
            success_count += 1
            log.info(f"AI Patcher: Successfully updated '{abs_path}'.")

        except IOError as e:
            msg = f"Failed to write to '{abs_path}': {e}"
            log.error(f"AI Patcher: {msg}")
            errors.append(msg)
        except Exception as e:
            msg = f"An unexpected error occurred for '{abs_path}': {e}"
            log.error(f"AI Patcher: {msg}", exc_info=True)
            errors.append(msg)

    final_message = f"Successfully updated {success_count} file(s)."
    if errors:
        final_message += "\n\nEncountered the following errors:\n" + "\n".join(f"- {e}" for e in errors)
        return False, final_message

    return True, final_message