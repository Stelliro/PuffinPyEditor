# PuffinPyEditor/plugins/json_tools/plugin_main.py
from .json_syntax_highlighter import JsonSyntaxHighlighter
from utils.logger import log


class JsonToolsPlugin:
    """
    A simple plugin to register the JSON syntax highlighter.
    """
    def __init__(self, puffin_api):
        self.api = puffin_api
        self.api.register_highlighter('.json', JsonSyntaxHighlighter)
        log.info("JSON Tools: Registered highlighter for .json files.")


def initialize(puffin_api):
    """Entry point for PuffinPyEditor to load the plugin."""
    return JsonToolsPlugin(puffin_api)