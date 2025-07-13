# /plugins/ai_patcher/response_parser.py
import os
import re
from typing import Dict, Tuple
from utils.logger import log

def parse_llm_response(response_text: str) -> Dict[str, str]:
    """
    Parses a markdown response from an LLM using a state machine to robustly
    handle file blocks and unassigned code blocks.
    """
    changes: Dict[str, str] = {}
    lines = response_text.splitlines()

    # Define states for the Finite State Machine (FSM)
    STATE_IDLE = 0           # Looking for a header or start of any code block
    STATE_IN_BLOCK = 1       # Inside a ``` code block

    state = STATE_IDLE
    current_path: Optional[str] = None
    current_content: List[str] = []
    unspecified_counter = 0

    header_pattern = re.compile(r"^\s*###\s+File:\s+`?(.*?)`?\s*$")

    i = 0
    while i < len(lines):
        line = lines[i]
        
        if state == STATE_IDLE:
            header_match = header_pattern.match(line)
            is_fence = line.strip().startswith('```')

            if header_match:
                path = header_match.group(1).strip()
                # Find the next line that is a code fence
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith('```'):
                    j += 1
                
                if j < len(lines): # Opening fence found
                    current_path = path if (path and path != "/") else None
                    if current_path:
                        state = STATE_IN_BLOCK
                        i = j  # Move pointer past the opening fence
                    else:
                        log.warning(f"AI Patcher: Ignoring invalid file path found in header: '{header_match.group(1)}'")
                else: # Header without a block, ignore
                    log.warning(f"AI Patcher: Found file header for '{path}' but no subsequent code block. Ignoring header.")
            
            elif is_fence:
                # Code block without a preceding header
                unspecified_counter += 1
                current_path = f"[UNSPECIFIED_FILE_{unspecified_counter}]"
                state = STATE_IN_BLOCK

        elif state == STATE_IN_BLOCK:
            if line.strip().startswith('```'):
                # Closing fence, end of block
                if current_path:
                    changes[current_path] = "\n".join(current_content)
                    log.info(f"AI Patcher: Parsed block for '{current_path}'.")
                
                # Reset for next block
                state = STATE_IDLE
                current_path = None
                current_content = []
            else:
                current_content.append(line)
        
        i += 1

    # If the response ends with an unterminated block, save what we have.
    if state == STATE_IN_BLOCK and current_path:
        log.warning(f"AI Patcher: Response ended with an unterminated code block for '{current_path}'. Including content.")
        changes[current_path] = "\n".join(current_content)
        
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
        return False, "No file changes were found to apply."

    errors = []
    success_count = 0

    for rel_path, content in changes.items():
        # Skip unspecified files that may have been parsed but not assigned a path.
        if rel_path.startswith("[UNSPECIFIED_FILE_"):
            log.warning(f"AI Patcher: Skipped applying unassigned content block '{rel_path}'.")
            continue
            
        clean_rel_path = rel_path.lstrip('/').lstrip('\\')
        abs_path = os.path.join(project_root, clean_rel_path)

        if not os.path.abspath(abs_path).startswith(os.path.abspath(project_root)):
            msg = f"Skipped unsafe path: '{rel_path}' resolves outside the project directory."
            log.error(f"AI Patcher: {msg}")
            errors.append(msg)
            continue

        try:
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