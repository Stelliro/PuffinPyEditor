# PuffinPyEditor/plugins/list_view_explorer/icon_provider.py
from PyQt6.QtWidgets import QFileIconProvider
from PyQt6.QtCore import QFileInfo
import qtawesome as qta
from app_core.puffin_api import PuffinPluginAPI


class CustomFileIconProvider(QFileIconProvider):
    BINARY_EXTENSIONS = {'.exe', '.dll', '.so', '.o', '.a', '.lib', '.dylib', '.app', '.msi'}
    ICON_MAP = {
        ".git": "mdi.git", "__pycache__": "mdi.folder-cog-outline", "venv": "mdi.folder-cog-outline",
        ".venv": "mdi.folder-cog-outline", "dist": "mdi.folder-zip-outline", "build": "mdi.folder-zip-outline",
        "node_modules": "mdi.folder-npm-outline", "logs": "mdi.folder-text-outline",
        "tests": "mdi.folder-search-outline", "test": "mdi.folder-search-outline",
        ".vscode": "mdi.folder-vscode", ".idea": "mdi.folder-cog-outline",
        "Dockerfile": "mdi.docker", ".dockerignore": "mdi.docker", "docker-compose.yml": "mdi.docker",
        ".gitignore": "mdi.git", ".gitattributes": "mdi.git", "pyproject.toml": "mdi.language-python",
        "poetry.lock": "mdi.language-python", "requirements.txt": "mdi.format-list-numbered",
        "package.json": "mdi.npm", "package-lock.json": "mdi.npm", "pnpm-lock.yaml": "mdi.npm", "yarn.lock": "mdi.npm",
        ".env": "mdi.key-variant", ".env.example": "mdi.key-outline",
        "README.md": "mdi.book-open-variant",
        ".py": "mdi.language-python", ".pyc": "mdi.language-python", ".pyw": "mdi.language-python",
        ".js": "mdi.language-javascript", ".mjs": "mdi.language-javascript", ".ts": "mdi.language-typescript",
        ".tsx": "mdi.language-typescript", ".java": "mdi.language-java", ".jar": "mdi.language-java",
        ".cs": "mdi.language-csharp", ".csproj": "mdi.language-csharp", ".cpp": "mdi.language-cpp",
        ".hpp": "mdi.language-cpp", ".c": "mdi.language-c", ".h": "mdi.language-c",
        ".rs": "mdi.language-rust", ".go": "mdi.language-go", ".rb": "mdi.language-ruby",
        ".php": "mdi.language-php", ".swift": "mdi.language-swift", ".kt": "mdi.language-kotlin",
        ".sh": "mdi.bash", ".bat": "mdi.powershell", ".ps1": "mdi.powershell",
        ".html": "mdi.language-html5", ".htm": "mdi.language-html5", ".css": "mdi.language-css3",
        ".scss": "mdi.language-css3", ".json": "mdi.code-json", ".xml": "mdi.xml",
        ".yaml": "mdi.yaml", ".yml": "mdi.yaml", ".toml": "mdi.cog-outline", ".ini": "mdi.cog-outline",
        ".cfg": "mdi.cog-outline", ".conf": "mdi.cog-outline", ".sql": "mdi.database", ".db": "mdi.database",
        ".sqlite3": "mdi.database", ".md": "mdi.markdown", ".txt": "mdi.file-document-outline",
        ".log": "mdi.file-document-outline", ".pdf": "mdi.file-pdf-box", ".rtf": "mdi.file-word",
        ".docx": "mdi.file-word", ".csv": "mdi.file-delimited-outline", ".xls": "mdi.file-excel",
        ".xlsx": "mdi.file-excel", ".zip": "mdi.folder-zip-outline", ".rar": "mdi.folder-zip-outline",
        ".7z": "mdi.folder-zip-outline", ".tar": "mdi.folder-zip-outline", ".gz": "mdi.folder-zip-outline",
        ".bz2": "mdi.folder-zip-outline", ".png": "mdi.file-image", ".jpg": "mdi.file-image",
        ".jpeg": "mdi.file-image", ".gif": "mdi.file-image", ".bmp": "mdi.file-image",
        ".ico": "mdi.file-image", ".svg": "mdi.svg",
    }

    def __init__(self, puffin_api: PuffinPluginAPI):
        super().__init__()
        self.api = puffin_api

    def icon(self, fileInfoOrType):
        # The argument can be a QFileInfo object or an IconType enum.
        # We only care about QFileInfo for our custom logic.
        if not isinstance(fileInfoOrType, QFileInfo):
            # This handles cases where Qt asks for generic icons like Folder, Computer etc.
            # We use the correct enum for this check.
            if isinstance(fileInfoOrType, QFileIconProvider.IconType):
                return super().icon(fileInfoOrType)
            # Fallback for unexpected types
            return qta.icon('fa5s.file')

        file_info = fileInfoOrType
        main_window = self.api.get_main_window()
        if not main_window: return qta.icon('fa5s.file')

        theme_manager = main_window.theme_manager
        # Ensure we have a valid theme data structure to prevent crashes if theme fails
        theme_data = theme_manager.current_theme_data or {}
        colors = theme_data.get('colors', {})
        icon_colors = colors.get('icon.colors', {})
        
        default_folder_color = icon_colors.get('default_folder', '#79b8f2')
        default_file_color = icon_colors.get('default_file', '#C0C5CE')

        if file_info.isDir():
            folder_name = file_info.fileName()
            icon_name = self.ICON_MAP.get(folder_name, 'mdi.folder-outline')
            color = icon_colors.get(folder_name, default_folder_color)
            return qta.icon(icon_name, color=color)

        file_name = file_info.fileName()
        extension = f".{file_info.suffix().lower()}"

        if file_name in self.ICON_MAP:
            icon_name = self.ICON_MAP[file_name]
            color = icon_colors.get(file_name, default_file_color)
            return qta.icon(icon_name, color=color)
        if extension in self.BINARY_EXTENSIONS:
            return qta.icon('mdi.cog', color=default_file_color)
        if extension in self.ICON_MAP:
            icon_name = self.ICON_MAP[extension]
            color = icon_colors.get(extension, default_file_color)
            return qta.icon(icon_name, color=color)
        
        # Fallback to the default system icon if no match is found
        return super().icon(file_info)