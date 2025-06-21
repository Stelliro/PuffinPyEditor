# PuffinPyEditor/ui/widgets/syntax_highlighter.py
import re
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import Qt
from utils.logger import log
from app_core.theme_manager import theme_manager


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.highlighting_rules = []
        self.initialize_formats()
        self.setup_rules()
        log.info("PythonSyntaxHighlighter initialized.")

    def initialize_formats(self):
        self.formats = {}
        current_colors = {}
        if theme_manager and theme_manager.current_theme_data and "colors" in theme_manager.current_theme_data:
            current_colors = theme_manager.current_theme_data["colors"]
        else:
            log.warning(
                "SyntaxHighlighter: current_theme_data or its 'colors' key is not available. Using fallbacks for formats.")
            current_colors = theme_manager._get_default_fallback_theme().get("colors", {})

        def create_format(key_name, default_color_hex, bold=False, italic=False):
            color_hex = current_colors.get(f"syntax.{key_name}", default_color_hex)
            try:
                color = QColor(color_hex)
            except Exception as e:
                log.warning(
                    f"Invalid color hex '{color_hex}' for 'syntax.{key_name}'. Using default {default_color_hex}. Error: {e}")
                color = QColor(default_color_hex)

            text_format = QTextCharFormat()
            text_format.setForeground(color)
            if bold:
                text_format.setFontWeight(QFont.Weight.Bold)
            if italic:
                text_format.setFontItalic(italic)
            return text_format

        self.formats["keyword"] = create_format("keyword", "#569CD6", bold=True)
        self.formats["operator"] = create_format("operator", "#D4D4D4")
        self.formats["brace"] = create_format("brace", "#FFD700")
        self.formats["decorator"] = create_format("decorator", "#B5CEA8", italic=True)
        self.formats["self"] = create_format("self", "#C586C0", italic=True)
        self.formats["className"] = create_format("className", "#4EC9B0", bold=True)
        self.formats["functionName"] = create_format("functionName", "#DCDCAA")
        self.formats["comment"] = create_format("comment", "#6A9955", italic=True)
        self.formats["string"] = create_format("string", "#CE9178")
        self.formats["docstring"] = create_format("docstring", "#CE9178", italic=True)
        self.formats["number"] = create_format("number", "#B5CEA8")

        self.multiline_string_format = self.formats["docstring"]

        theme_display_name = "UnknownTheme"
        current_theme_id_for_log = "unknown_id"
        if theme_manager:
            current_theme_id_for_log = theme_manager.current_theme_id
            if theme_manager.current_theme_data and isinstance(theme_manager.current_theme_data, dict):
                theme_display_name = theme_manager.current_theme_data.get('name', current_theme_id_for_log)

        log.debug(
            f"Syntax highlighter formats initialized/updated with theme ID: {current_theme_id_for_log} (Name: {theme_display_name})")

    def setup_rules(self):
        self.highlighting_rules = []

        keywords = [
            r'\bdef\b', r'\bclass\b', r'\bif\b', r'\belif\b', r'\belse\b',
            r'\bfor\b', r'\bwhile\b', r'\breturn\b', r'\byield\b', r'\bpass\b',
            r'\bcontinue\b', r'\bbreak\b', r'\bimport\b', r'\bfrom\b', r'\bas\b',
            r'\btry\b', r'\bexcept\b', r'\bfinally\b', r'\braise\b', r'\bwith\b',
            r'\bassert\b', r'\bdel\b', r'\bglobal\b', r'\bnonlocal\b', r'\bin\b',
            r'\bis\b', r'\blambda\b', r'\bnot\b', r'\bor\b', r'\band\b',
            r'\bTrue\b', r'\bFalse\b', r'\bNone\b', r'\basync\b', r'\bawait\b'
        ]
        for pattern in keywords:
            self.highlighting_rules.append((re.compile(pattern), self.formats["keyword"]))
        self.highlighting_rules.append((re.compile(r'\bself\b'), self.formats["self"]))
        self.highlighting_rules.append((re.compile(r'@[A-Za-z0-9_]+'), self.formats["decorator"]))
        self.highlighting_rules.append((re.compile(r'\b[A-Z][A-Za-z0-9_]*'), self.formats["className"]))
        self.highlighting_rules.append((re.compile(r'\b[a-z_][A-Za-z0-9_]*(?=\()'), self.formats["functionName"]))
        self.highlighting_rules.append((re.compile(r'[+\-*/%=<>!&|^~]'), self.formats["operator"]))
        self.highlighting_rules.append((re.compile(r'[{}()\[\]]'), self.formats["brace"]))
        self.highlighting_rules.append((re.compile(r'\b[0-9]+\b'), self.formats["number"]))
        self.highlighting_rules.append((re.compile(r'\b0[xX][0-9a-fA-F]+\b'), self.formats["number"]))  # Hex
        self.highlighting_rules.append((re.compile(r'\b0[bB][01]+\b'), self.formats["number"]))  # Binary
        self.highlighting_rules.append(
            (re.compile(r'\b[0-9]+\.[0-9]*([eE][+-]?[0-9]+)?\b'), self.formats["number"]))
        self.highlighting_rules.append((re.compile(r'#.*'), self.formats["comment"]))
        self.highlighting_rules.append((re.compile(r"r?'.*?(?<!\\)'"), self.formats["string"]))
        self.highlighting_rules.append((re.compile(r'r?".*?(?<!\\)"'), self.formats["string"]))

        log.debug(f"Syntax highlighter rules set up. Total rules: {len(self.highlighting_rules)}")

    def highlightBlock(self, text: str) -> None:

        for pattern, text_format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start_index, end_index = match.span()
                self.setFormat(start_index, end_index - start_index, text_format)

        self.setCurrentBlockState(0)

        triple_single_quote_start_re = re.compile(r"r?'''")
        triple_double_quote_start_re = re.compile(r'r?"""')

        IN_TRIPLE_SINGLE = 1
        IN_TRIPLE_DOUBLE = 2

        if self.previousBlockState() == IN_TRIPLE_SINGLE:
            match = triple_single_quote_start_re.search(text)
            if match:
                end_offset = match.end()
                self.setFormat(0, end_offset, self.multiline_string_format)
                self.setCurrentBlockState(0)
            else:
                self.setFormat(0, len(text), self.multiline_string_format)
                self.setCurrentBlockState(IN_TRIPLE_SINGLE)
            return

        if self.previousBlockState() == IN_TRIPLE_DOUBLE:
            match = triple_double_quote_start_re.search(text)
            if match:
                end_offset = match.end()
                self.setFormat(0, end_offset, self.multiline_string_format)
                self.setCurrentBlockState(0)
            else:
                self.setFormat(0, len(text), self.multiline_string_format)
                self.setCurrentBlockState(IN_TRIPLE_DOUBLE)
            return


        match_double = triple_double_quote_start_re.search(text)
        match_single = triple_single_quote_start_re.search(text)

        start_offset = -1
        is_double_quoted = False

        if match_double and match_single:
            if match_double.start() < match_single.start():
                start_offset = match_double.start()
                is_double_quoted = True
            else:
                start_offset = match_single.start()
                is_double_quoted = False
        elif match_double:
            start_offset = match_double.start()
            is_double_quoted = True
        elif match_single:
            start_offset = match_single.start()
            is_double_quoted = False

        if start_offset != -1:
            end_re = triple_double_quote_start_re if is_double_quoted else triple_single_quote_start_re
            m_end = None
            search_from_pos = start_offset + 3
            if search_from_pos < len(text):
                m_end = end_re.search(text, search_from_pos)

            if m_end:
                end_offset = m_end.end()
                self.setFormat(start_offset, end_offset - start_offset, self.multiline_string_format)
                self.setCurrentBlockState(0)
            else:
                self.setFormat(start_offset, len(text) - start_offset, self.multiline_string_format)
                self.setCurrentBlockState(IN_TRIPLE_DOUBLE if is_double_quoted else IN_TRIPLE_SINGLE)

    def rehighlight_document(self):
        log.info("Re-highlighting entire document for syntax.")
        self.initialize_formats()
        self.setup_rules()
        super().rehighlight()


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication, QPlainTextEdit

    if QApplication.instance() is None:
        app = QApplication([])
    else:
        app = QApplication.instance()
    editor_for_test = QPlainTextEdit()
    log.info(
        f"Syntax Highlighter Test: Using theme: {theme_manager.current_theme_name if theme_manager else 'Unknown'}")

    highlighter = PythonSyntaxHighlighter(editor_for_test.document())

    test_code = """
# This is a comment
class MyClass(SomeBaseClass):
    '''This is a
    multi-line docstring.'''
    def __init__(self, value=123, name="Test"): # constructor
        self.value = value  # An instance variable
        self.name: str = name # type hint
        super().__init__()
        print(f"Initialized with {value} and '{name}'") # f-string

    @classmethod
    def create(cls):
        '''Another docstring.
        Continues here.'''
        return cls(value=0xABC, name=r"Raw\\String")

    def _my_method(self, param1, param2=None):
        if param1 > 10.5 and (param2 is not None or self.value == True):
            try:
                result = param1 / param2 if param2 != 0 else float('inf')
            except TypeError:
                result = None
            return result
        elif param1 == 0b101: # Binary
            return "Binary five"
        else:
            # Single quotes
            text = 'hello world \\' escapes work too'
            raw_text = r'no escapes here'
            return None
"""
    editor_for_test.setPlainText(test_code)
    editor_for_test.setWindowTitle("Syntax Highlighter Test")
    editor_for_test.resize(600, 400)
    editor_for_test.show()

    sys.exit(app.exec())