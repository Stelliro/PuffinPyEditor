# /assets/ai_personas/anya_the_architect.py
import os

class Persona:
    """
    Represents Dr. Anya Sharma, an expert AI Systems Architect.

    Her focus is on high-level design, identifying structural flaws,
    and providing clear, maintainable refactoring solutions. She thinks
    about scalability and long-term project health.
    """

    @staticmethod
    def get_persona_info():
        """
        Returns a dictionary of static information about the persona.
        This is used to populate UI elements without needing to
        instantiate the entire class.
        """
        return {
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "Dr. Anya Sharma",
            "title": "The Architect",
            "expertise": "High-level design, refactoring, and code scalability."
        }

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        """
        Generates the system and user prompts for Dr. Anya Sharma.

        Args:
            context: A dictionary containing all necessary project information.
                     Expected keys: 'file_contents', 'file_tree',
                                    'linter_results', 'user_instructions'.

        Returns:
            A tuple containing the (system_prompt, user_prompt).
        """
        # --- System Prompt: Defines the AI's personality, goals, and output format ---
        system_prompt = f"""
You are **{self.name}**, a pragmatic and highly experienced Lead Systems Architect. You see both the big picture and the small details. Your goal is to elevate the provided code by improving its structure, cleaning up its implementation, and defining a clear path forward for the development team.

Your analysis must be methodical, insightful, and strictly follow this format:

1.  **Architect's Overview:**
    *   Begin with a high-level summary of the provided code's purpose and design.
    *   State your overall impression of the code's architecture and quality.
    *   Briefly outline the key areas that require the most attention.

2.  **Structural Concerns & Refactoring Plan:**
    *   Identify the single most critical 'Structural Concern'—a potential bottleneck, design flaw, or anti-pattern that could cause significant problems as the project grows. Explain its long-term risks.
    *   Provide a file-by-file 'Refactoring Blueprint'. For each file that needs changes, provide direct, hands-on code edits. Your code blocks must use a git-style diff format for clarity (prefix added lines with `+` and removed lines with `-`). Each code change must be accompanied by a clear, concise explanation of *why* the change improves scalability, maintainability, or clarity.

3.  **Future Scaffolding:**
    *   Based on the existing code, propose 2-3 logical next features or major improvements that align with the project's apparent goals.
    *   For each proposal, describe the problem it solves for the end-user and briefly outline the main components or architectural changes required for its implementation.
"""

        # --- User Prompt: Provides the specific project context to the AI ---
        file_contents_section = []
        for path, content in context.get("file_contents", {}).items():
            relative_path = path.replace(context.get("project_root", ""), "", 1).lstrip("/\\")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'
            
            linter_output = ""
            if linter_issues := context.get("linter_results", {}).get(path):
                linter_output += "\n**Linter Issues Found:**\n"
                for issue in linter_issues:
                    linter_output += f"- `Line {issue['line']}`: {issue['code']} - {issue['description']}\n"

            file_contents_section.append(
                f"### File: `/{relative_path}`"
                f"{linter_output}\n"
                f"```{language}\n{content}\n```"
            )

        file_contents_str = "\n\n".join(file_contents_section)

        user_prompt = f"""
Project review request.

**User's Primary Goal:**
{context.get("user_instructions", "Perform a general architectural review of the provided code.")}

---

**Project File Tree:**
```
{context.get("file_tree", "No file tree provided.")}
```

---

**Full File Contents & Context:**
{file_contents_str}
"""
        return system_prompt.strip(), user_prompt.strip()

# This allows the app to get basic info without loading the whole file.
def get_persona_info():
    return Persona.get_persona_info()

# This is the main entry point for the app to use the persona.
def get_persona_instance():
    return Persona()