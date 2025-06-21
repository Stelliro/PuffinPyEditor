# 🐧 PuffinPyEditor

**A Modern, Extensible Python IDE built with PyQt6**

PuffinPyEditor is a lightweight yet powerful Integrated Development Environment designed for Python developers. Built from the ground up using Python and the PyQt6 framework, it aims to provide a clean, modern, and highly customizable coding experience. It's perfect for developers who want a fast, native tool that integrates essential features like version control, a built-in terminal, and a dynamic plugin system, without the overhead of larger IDEs.



## ✨ Key Features

PuffinPyEditor is packed with features designed to streamline your development workflow:

#### 📝 Core Editor
*   **Syntax Highlighting:** Full Python syntax highlighting that adapts to your chosen theme.
*   **Code Completion & IntelliSense:** Smart code suggestions, function signature hints, and tooltips powered by the Jedi engine.
*   **Go to Definition:** Instantly jump to the definition of a class, function, or variable (`F12`).
*   **Advanced Editing:** Line numbers, auto-indentation, automatic bracket and quote pairing, and multi-line editing.
*   **Find & Replace:** A familiar and powerful dialog for searching within files.

#### 🗂️ Project and File Management
*   **Tabbed Project Management:** Open multiple project folders in a tabbed sidebar for easy switching.
*   **File System Explorer:** A full-featured file tree with a context menu to create, rename, and delete files and folders.
*   **Drag and Drop:** Move files and folders within the project tree.
*   **AI Export Tool:** A unique feature under the `Tools` menu to concatenate your entire project's source code into a single Markdown file, perfect for analysis by large language models.

#### 🔧 Integrated Tools
*   **Dockable Panels:** A flexible UI where you can rearrange the Terminal, Problems, Output, and Source Control panels.
*   **Built-in Terminal:** A fully interactive terminal that opens in your project's root directory, with automatic virtual environment (`venv`) activation.
*   **Code Runner:** Execute Python scripts directly from the editor (`F5`) and see their output in the Output panel.
*   **Linter Integration:** On-the-fly code analysis using `flake8`, with errors and warnings displayed in the "Problems" panel.

#### 🐙 Source Control & GitHub Integration
*   **Git Aware:** The "Source Control" panel automatically detects Git repositories.
*   **Core Git Actions:** View changed files, stage them for commit, and commit your work with a message. Push and pull to/from your remotes with the click of a button.
*   **GitHub Integration:**
    *   A "Manage Remotes" dialog allows you to list your GitHub repositories, view branches, and clone them directly to your machine.
    *   Create new public or private repositories on GitHub from within the app.
    *   **Publish Project:** For a local project not yet on Git, a "Publish" button will create a new GitHub repository and push your project to it in one go.

#### 🎨 Customization
*   **Powerful Theme Manager:** Comes with a curated set of light and dark themes. The advanced **Theme Customizer** allows you to edit any theme and save your own creations.
*   **Extensive Preferences:** Customize everything from font family and size to indentation settings (tabs vs. spaces) and auto-save behavior.

#### 🔌 Extensible Plugin System
*   **Dynamic Plugin Loading:** Add new features and tools to the editor without modifying the core source code.
*   **Plugin Management UI:** Install new plugins by fetching them from a GitHub repository or by uploading a local `.zip` file directly through the Preferences menu.

## 🚀 Getting Started

PuffinPyEditor is a standalone desktop application. To run it from the source, you will need `Python 3` and `Git` installed on your system.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/PuffinPyEditor.git
    cd PuffinPyEditor
    ```

2.  **Create a Virtual Environment:**
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

## 🧩 The Plugin System

PuffinPyEditor can be extended with custom plugins located in the `/plugins` directory.

#### For Users
You can install new plugins easily:
1.  Navigate to `File > Preferences > Plugins`.
2.  **From GitHub:** Enter a repository URL (like `gike5/puffin-plugins`) and click "Fetch" to see a list of available plugins.
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
        "entry_point": "main.py"
    }
    ```
2.  **`main.py`** (or your specified `entry_point`): The Python file with your plugin's logic. It must contain an `initialize(main_window)` function.
    ```python
    from PyQt6.QtGui import QAction
    
    def initialize(main_window):
        # main_window is an instance of the MainWindow class
        action = QAction("Do Awesome Thing", main_window)
        action.triggered.connect(lambda: print("Awesome thing done!"))
        
        # You can access existing menus or create new ones
        main_window.tools_menu.addAction(action)
    ```

## 🤝 Contributing
Contributions are welcome! Whether it's reporting a bug, suggesting a new feature, or submitting a pull request, your help is appreciated. Please feel free to open an issue to discuss your ideas.

## 📜 License
This project is licensed under the MIT License - see the `LICENSE` file for details.