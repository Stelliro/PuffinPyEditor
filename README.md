<<<<<<< HEAD
<<<<<<< HEAD
# 🐧 PuffinPyEditor

**DEVELOPED WITH AI**

**A Modern, Extensible Python IDE built with PyQt6 and a lot of passion.**

PuffinPyEditor is a lightweight yet powerful Integrated Development Environment for Python developers. Built from the ground up using Python and the PyQt6 framework, it aims to provide a clean, modern, and highly customizable coding experience. It's perfect for developers who want a fast, native-feeling tool that integrates essential features like version control, a built-in terminal, and a dynamic plugin system, without the overhead of larger IDEs.

### Why PuffinPyEditor?

*   **For Python, By Python:** The entire application is a testament to what's possible with Python, using the powerful PyQt6 framework for its native UI.
*   **Lightweight & Fast:** Starts quickly and stays responsive. PuffinPyEditor focuses on providing the essential tools you need without the bloat.
*   **You're in Control:** With a deep theme customizer, extensive preferences, and a simple plugin system, you can tailor the editor to your exact workflow and aesthetic.

## ✨ Key Features

---

#### 📝 **Modern Code Editor**
*   **Advanced Syntax Highlighting:** Full Python syntax highlighting that adapts instantly to your chosen theme.
*   **Intelligent Code Completion:** Smart suggestions, function signature hints, and detailed tooltips powered by the Jedi engine.
*   **Go to Definition:** Instantly jump to the definition of any class, function, or variable with a single keypress (`F12`).
*   **Efficient Text Editing:** Enjoy modern editor features like line numbers, auto-indentation (tabs or spaces), automatic bracket/quote pairing, and multi-line editing.
*   **Powerful Find & Replace:** A familiar and robust dialog for searching within files, with support for case sensitivity, whole words, and more.

---

#### 🗂️ **Full Project & File Management**
*   **Tabbed Project Management:** Open multiple project folders in a tabbed sidebar, allowing you to switch between different contexts effortlessly.
*   **Intuitive File Explorer:** A full-featured file tree with a context menu to create, rename, and delete files and folders directly within the editor.
*   **Drag and Drop:** Easily reorganize your project by dragging and dropping files and folders within the file tree.

---

#### 🤖 **Advanced AI Export**
*   **Intelligent Context Creation:** A powerful tool under the `Tools` menu designed to package your project for analysis by Large Language Models (LLMs) like GPT, Claude, or Gemini.
*   **Selective File Inclusion:** Don't send your entire project. Use the built-in file tree to select exactly which files and folders should be included in the export, keeping the context clean and relevant.
*   **Custom Instructions & Guidelines:** Guide the AI's analysis by providing detailed instructions and a list of specific rules or guidelines for it to follow.
*   **Reusable Prompt Loadouts:**
    *   Comes with pre-packaged loadouts for common tasks like "Code Review," "Documentation Generation," and "Refactoring Suggestions."
    *   Create and save your own custom loadouts for your unique workflows.
    *   Easily load, update, and delete your saved prompts, streamlining your interaction with AI.
*   **Integrated Linter Results:** The export automatically includes `flake8` linter results for each selected Python file, giving the AI immediate insight into code quality issues.

---

#### 🔧 **Integrated Tooling**
*   **Flexible Dockable UI:** Rearrange the Terminal, Problems, Output, and Source Control panels to create a layout that works for you.
*   **Built-in Terminal:** A fully interactive terminal that opens in your project's root directory. It automatically detects Python virtual environments (`venv`) for a seamless workflow.
*   **One-Click Code Runner:** Execute Python scripts directly from the editor (`F5`) and see their output in the dedicated Output panel.
*   **Live Linter Integration:** Get on-the-fly code analysis using `flake8`. Errors and warnings are clearly displayed in the "Problems" panel, allowing you to jump straight to the issue.

---

#### 🐙 **Deep Source Control & GitHub Integration**
*   **Git Aware:** The "Source Control" panel automatically detects Git repositories and shows you changed files at a glance.
*   **Core Git Actions:** Stage changes, commit your work with a message, and push and pull to/from your remotes with the click of a button.
*   **Seamless GitHub Workflow:**
    *   **Publish Project:** Have a local project that's not on Git? The "Publish" button will create a new GitHub repository and push your project to it in one go.
    *   **Clone & Manage:** The GitHub dialog allows you to list your personal repositories, view their branches, and clone them directly to your machine.
    *   **Create Releases:** Create new versioned releases on GitHub, complete with tags, notes, and asset uploads, all from within the app.

---

#### 🎨 **Powerful Customization**
*   **Advanced Theme Manager:** PuffinPyEditor comes with a curated set of light and dark themes. The powerful **Theme Customizer** allows you to edit any theme, tweak every color, and save your own unique creations.
*   **Extensive Preferences:** Customize everything from font family and size to indentation settings (tabs vs. spaces) and auto-save behavior.

---

#### 🔌 **Simple & Extensible Plugin System**
*   **Dynamic Plugin Loading:** Add new features and tools to the editor without ever touching the core source code.
*   **Easy Plugin Management:** Install new plugins by fetching them from a GitHub repository or by uploading a local `.zip` file directly through the Preferences menu.

## 🚀 Getting Started

### Using the Installer (Windows)
The easiest way to get started on Windows is to download the latest setup executable from the [**Releases**](https://github.com/Stelliro/PuffinPyEditor/releases) page. The installer provides options for creating desktop and Start Menu shortcuts.

### Running from Source
To run the editor from the source code, you will need `Python 3` and `Git` installed on your system.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Stelliro/PuffinPyEditor.git
    cd PuffinPyEditor
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Editor:**
    ```bash
    python main.py
    ```

## 📦 Creating a Windows Installer

A Windows installer can be created using the provided `build.bat` script. This process bundles the application into a standalone executable and then packages it into a themed, user-friendly setup file.

#### Prerequisites

1.  **NSIS:** You must have [NSIS (Nullsoft Scriptable Install System)](https://nsis.sourceforge.io/Download) installed. During installation, make sure to allow it to be added to your system's PATH.
2.  **Project Dependencies:** Ensure you have installed all the project's Python dependencies by running `pip install -r requirements.txt`.

#### Build Steps

1.  Open a command prompt in the root directory of the project.
2.  Run the build script:
    ```bash
    .\installer\build.bat
    ```
3.  The script will:
    *   Verify that `pyinstaller` and `makensis` are available.
    *   Run PyInstaller to bundle the application into the `/dist/PuffinPyEditor` directory.
    *   Run NSIS to compile the installer using the script and assets in the `/installer` directory.
4.  Once complete, the final setup file (e.g., `PuffinPyEditor_v1.2.0_Setup.exe`) will be located in the `/dist` directory.

## 🔒 Security & Privacy

**Important:** The editor stores your personal settings, including your GitHub access token and AI Export loadouts, in a file named `puffin_editor_settings.json` in the project's root directory.

*   This file is **automatically ignored by Git** thanks to the `.gitignore` file. You should **never** commit this file to a public repository.
*   The "Export for AI" and "Create Release" tools are also configured to **exclude** this file automatically.
*   Always be mindful not to hard-code sensitive information like passwords or API keys directly into your source code.

## 🧩 The Plugin System

PuffinPyEditor can be extended with custom plugins located in the `/plugins` directory.

**🔒 Security Warning:** Plugins are powerful and execute with the same permissions as the editor itself. For your security, **only install plugins from authors and sources you trust.** PuffinPyEditor cannot vet the safety or integrity of third-party plugins.

#### For Users
You can install new plugins easily:
1.  Navigate to `File > Preferences > Plugins`.
2.  **From GitHub:** Enter a repository URL (like `Stelliro/puffin-plugins`) and click "Fetch" to see a list of available plugins.
3.  **From a File:** Click "Install from File..." to upload a `.zip` archive of a plugin.
4.  After installation, a restart will be required to load the new plugin.

#### For Developers
Creating a plugin is simple. Each plugin lives in its own subdirectory inside `/plugins` and must contain two files:
1.  **`plugin.json`**: A manifest file describing your plugin.
    ```json
    {
        "name": "My Awesome Plugin",
        "author": "Your Name",
        "version": "1.0.0",
        "description": "This plugin does awesome things.",
        "entry_point": "plugin_main.py"
    }
    ```
2.  **`plugin_main.py`** (or your specified `entry_point`): The Python file with your plugin's logic. It must contain an `initialize(main_window)` function.
    ```python
    from PyQt6.QtGui import QAction
    
    def initialize(main_window):
        # main_window is an instance of the MainWindow class
        action = QAction("Do Awesome Thing", main_window)
        action.triggered.connect(lambda: print("Awesome thing done!"))
        
        # You can access existing menus or create new ones
        main_window.tools_menu.addAction(action)

        # The function should return the plugin instance if it needs to persist
        return None 
    ```

## 🤝 Contributing
Contributions are welcome! Whether it's reporting a bug, suggesting a new feature, or submitting a pull request, your help is appreciated. Please feel free to open an issue to discuss your ideas.

## 📜 License
This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License**.

In short, you are free to share and adapt the material for **non-commercial purposes**, as long as you give appropriate credit and distribute your contributions under the same license. For the full license text, please see the `LICENSE.md` file.
=======
=======
>>>>>>> 3a3f3c7791dc5b872454b8fc93e7230d2014e032
# PuffinPyEditor Plugin Distribution Repository
This repository is structured to serve plugins for the PuffinPyEditor.
- `index.json`: A manifest file listing all available plugins and their download URLs.
- `zips/`: This directory contains the packaged `.zip` files for each plugin.
To publish a new version of a plugin, use the "Publish Plugin" tool inside PuffinPyEditor.
<<<<<<< HEAD
>>>>>>> 3a3f3c7791dc5b872454b8fc93e7230d2014e032
=======
>>>>>>> 3a3f3c7791dc5b872454b8fc93e7230d2014e032
