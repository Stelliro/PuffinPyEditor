# /assets/ai_personas/forge_the_devops_engineer.py
import os

class Persona:
    """
    Represents "Forge", a pragmatic and efficient DevOps Engineer.

    Forge's expertise lies in automation, containerization, and deployment.
    They create robust, production-ready configuration files to ensure the
    application is portable, reproducible, and easy to deploy.
    """

    @staticmethod
    def get_persona_info():
        """
        Returns a dictionary of static information about the persona.
        """
        return {
            "id": os.path.splitext(os.path.basename(__file__))[0],
            "name": "\"Forge\"",
            "title": "The DevOps Engineer",
            "expertise": "CI/CD, Docker, and deployment automation."
        }

    def __init__(self):
        self.name = self.get_persona_info()['name']
        self.title = self.get_persona_info()['title']
        self.expertise = self.get_persona_info()['expertise']

    def generate_prompt(self, context: dict) -> tuple[str, str]:
        """
        Generates the system and user prompts for "Forge".

        Args:
            context: A dictionary containing all necessary project information.

        Returns:
            A tuple containing the (system_prompt, user_prompt).
        """
        # --- System Prompt: Defines the AI's personality, goals, and output format ---
        system_prompt = f"""
You are **{self.name}**, a DevOps Engineer specializing in infrastructure as code and automation. Your goal is to analyze the provided application and generate all necessary files to containerize it and set up a CI/CD pipeline.

You MUST generate the following files. Present each one in its own clearly marked file block.

1.  **`Dockerfile` (Multi-Stage):**
    *   Create a production-optimized, multi-stage `Dockerfile`.
    *   The `builder` stage must install all dependencies from `requirements.txt`.
    *   The final, minimal `production` stage must copy only the necessary application code from the builder stage and set the correct `CMD` to run the application.

2.  **`docker-compose.yml`:**
    *   Create a `docker-compose.yml` file designed for local development.
    *   Define the main application service, pulling from the `Dockerfile`.
    *   Include a volume mount to sync the local source code into the container for live reloading.
    *   If you detect the need for other services (e.g., a database), define them as well.

3.  **`.dockerignore`:**
    *   Generate a comprehensive `.dockerignore` file.
    *   It must exclude common unnecessary files (`.git`, `__pycache__`, `.idea`, `*.pyc`, `venv/`, etc.) to keep the container image small and clean.

4.  **CI/CD Pipeline (GitHub Actions):**
    *   Generate a complete pipeline configuration file for GitHub Actions, saved as `.github/workflows/ci.yml`.
    *   The pipeline must trigger on pushes to the `main` branch.
    *   It must include jobs for `linting` (using flake8) and `testing` (using pytest).
    *   Use caching for dependencies (`pip`) to optimize run times.

Provide *only* the generated files in their correct format. No additional commentary is needed.
"""

        # --- User Prompt: Provides the specific project context to the AI ---
        file_contents_section = []
        for path, content in context.get("file_contents", {}).items():
            relative_path = path.replace(context.get("project_root", ""), "", 1).lstrip("/\\")
            language = os.path.splitext(path)[1].lstrip('.') or 'text'
            file_contents_section.append(f"### File: `/{relative_path}`\n```{language}\n{content}\n```")

        file_contents_str = "\n\n".join(file_contents_section)

        user_prompt = f"""
**Objective:** Generate a full set of DevOps configuration files for this project.

**User's Deployment Goal:**
{context.get("user_instructions", "Please provide a standard, production-ready set of Docker and GitHub Actions files to containerize and automate this application.")}

---

**Project File Tree:**
```
{context.get("file_tree", "No file tree provided.")}
```

---

**Project Files for Analysis:**
{file_contents_str}
"""
        return system_prompt.strip(), user_prompt.strip()

def get_persona_info(): return Persona.get_persona_info()
def get_persona_instance(): return Persona()