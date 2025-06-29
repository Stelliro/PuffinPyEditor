# PuffinPyEditor/plugins/ai_quick_actions/plugin_main.py
from functools import partial
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal

from plugins.ai_tools.api_client import ApiClient
from plugins.ai_tools.ai_response_dialog import AIResponseDialog


class AIWorker(QRunnable):
    """A runnable worker to execute AI API calls in a separate thread."""
    class Signals(QObject):
        finished = pyqtSignal(bool, str)

    def __init__(self, api_client, provider, model, system_prompt,
                 user_prompt):
        super().__init__()
        self.api_client = api_client
        self.provider = provider
        self.model = model
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.signals = self.Signals()

    def run(self):
        """Execute the request and emit the result."""
        success, response = self.api_client.send_request(
            self.provider, self.model, self.system_prompt, self.user_prompt
        )
        self.signals.finished.emit(success, response)


class AIQuickActionsPlugin:
    """Adds AI-powered actions to a new 'AI' top-level menu."""
    ACTIONS = [
        {
            "name": "Explain this code",
            "icon": "fa5s.question-circle",
            "system": (
                "You are an expert developer. Explain the following code "
                "snippet clearly and concisely. Describe its purpose, "
                "inputs, and outputs."
            ),
            "user": "Please explain this code:\n\n```python\n{selected_code}\n```"
        },
        {
            "name": "Suggest a refactoring",
            "icon": "fa5s.magic",
            "system": (
                "You are a senior developer focused on writing clean, "
                "efficient, and maintainable Python code. Refactor the "
                "following code snippet, explaining the key improvements "
                "you made."
            ),
            "user": "Please refactor this code:\n\n```python\n{selected_code}\n```"
        },
        {
            "name": "Find potential bugs",
            "icon": "fa5s.bug",
            "system": (
                "You are a quality assurance expert. Analyze the following "
                "code for potential bugs, logical errors, or edge cases "
                "that might not be handled correctly."
            ),
            "user": "Please find potential bugs in this code:\n\n```python\n{selected_code}\n```"
        }
    ]

    def __init__(self, main_window):
        self.api = main_window.puffin_api
        self.settings_manager = self.api.get_manager("settings")
        self.main_window = self.api.get_main_window()

        self.api_client = ApiClient(self.settings_manager)
        self.thread_pool = QThreadPool()

        for action_config in self.ACTIONS:
            callback = partial(self._run_action, action_config)
            self.api.add_menu_action(
                menu_name="ai",
                text=action_config["name"],
                callback=callback,
                icon_name=action_config["icon"]
            )

    def _run_action(self, config):
        """Callback executed when a menu action is clicked."""
        # Access the current editor widget via the central 'tabs' attribute
        # which is a standard name for a QTabWidget in the main window.
        current_editor = self.main_window.tabs.currentWidget()

        if not current_editor:
            self.api.show_message(
                "info", "No File Open", "Please open a file to use AI actions."
            )
            return

        selected_text = current_editor.textCursor().selectedText()
        if not selected_text:
            self.api.show_message(
                "info", "No Text Selected",
                "Please select some code to use this AI action."
            )
            return

        provider = "OpenAI"
        api_key = self.api_client.get_api_key(provider)
        if not api_key:
            QMessageBox.warning(
                self.api.get_main_window(),
                "API Key Missing",
                f"API Key for {provider} not found. Please go to "
                "Tools -> Manage API Keys... to add it."
            )
            return

        model = self.api_client.PROVIDER_CONFIG.get(
            provider, {}).get("models", [])[0]
        system_prompt = config["system"]
        user_prompt = config["user"].format(selected_code=selected_text)

        self.api.show_status_message(f"Sending selection to {model}...", 3000)

        worker = AIWorker(
            self.api_client, provider, model, system_prompt, user_prompt)
        worker.signals.finished.connect(self._on_action_finished)
        self.thread_pool.start(worker)

    def _on_action_finished(self, success, response):
        """Handles the response from the AI worker thread."""
        self.api.show_status_message("AI response received.", 2000)
        if success:
            dialog = AIResponseDialog(response, self.api.get_main_window())
            dialog.exec()
        else:
            QMessageBox.critical(
                self.api.get_main_window(), "API Error", response)


def initialize(main_window):
    return AIQuickActionsPlugin(main_window)