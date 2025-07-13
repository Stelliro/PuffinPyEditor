# /plugins/ai_tools/persona_logic.py
import os
from typing import List

def get_files_for_persona(persona_id: str, project_root: str) -> List[str]:
    """
    Gets a list of recommended files to select for a given persona.
    Returns an empty list if no specific logic exists for the persona,
    prompting the UI to select all files by default.
    """
    
    file_list = []
    
    # Logic for "Dr. Anya Sharma" - The Architect
    if persona_id == "anya_the_architect":
        # Architects are interested in high-level structure.
        # Select core application logic, main entry points, and managers.
        patterns = ['main.py', 'app_core/', 'ui/main_window.py', 'plugins/']
        for root, _, files in os.walk(project_root):
            for p in patterns:
                if f"/{p}" in root.replace(project_root, "").replace("\\", "/"):
                    for file in files:
                        if file.endswith('.py'):
                            file_list.append(os.path.join(root, file))

    # Logic for "Sofia Reyes" - The UX Visionary
    elif persona_id == "sofia_the_ux_visionary":
        # UX visionaries focus on the user interface.
        patterns = ['ui/', 'qss', '.css', '.html']
        for root, _, files in os.walk(project_root):
            for file in files:
                if any(p in os.path.join(root, file) for p in patterns) and file.endswith(('.py', '.qss', '.css', '.html')):
                     file_list.append(os.path.join(root, file))

    # Logic for "Glitch" - The QA Maverick
    elif persona_id == "glitch_the_qa_maverick":
        # QA needs to see the source code to write tests.
        # Exclude test files themselves to avoid testing the tests.
        for root, dirs, files in os.walk(project_root):
            # Exclude test directories from the walk
            dirs[:] = [d for d in dirs if 'test' not in d.lower()]
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_list.append(os.path.join(root, file))

    # Logic for "Eva the Sentinel" - The Security Expert
    elif persona_id == "eva_the_sentinel":
        # Security needs to see everything that could be an attack vector.
        # This includes requirements, configs, and all source code.
        patterns = ['.py', '.json', 'requirements.txt', '.cfg', '.ini']
        for root, _, files in os.walk(project_root):
             for file in files:
                 if any(file.endswith(p) for p in patterns):
                     file_list.append(os.path.join(root, file))

    # For other personas, return an empty list to indicate no specific preference.
    # The UI will default to selecting all files in this case.
    
    # Return a unique, sorted list of file paths
    return sorted(list(set(file_list)))