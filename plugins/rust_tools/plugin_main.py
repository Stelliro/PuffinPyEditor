# PuffinPyEditor/plugins/rust_tools/plugin_main.py
from .rust_syntax_highlighter import RustSyntaxHighlighter
from utils.logger import log

class RustToolsPlugin:
    """
    A plugin to register the Rust syntax highlighter.
    """
    def __init__(self, puffin_api):
        self.api = puffin_api
        self.api.register_highlighter('.rs', RustSyntaxHighlighter)
        log.info("Rust Tools: Registered highlighter for .rs files.")

def initialize(puffin_api):
    """
    Entry point for PuffinPyEditor to load the Rust Tools plugin.
    """
    # TODO: Implement business logic here, if any is needed beyond highlighting
    return RustToolsPlugin(puffin_api)