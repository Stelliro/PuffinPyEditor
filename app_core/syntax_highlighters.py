# PuffinPyEditor/app_core/syntax_highlighters.py
from typing import Dict, List, Tuple, Any
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from app_core.theme_manager import theme_manager
from utils.logger import log


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """
    A syntax highlighter for Python code that dynamically styles based on the
    current theme from the ThemeManager.
    """

    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_string_format = QTextCharFormat()

        self.initialize_formats_and_rules()
        log.info("PythonSyntaxHighlighter initialized from app_core.")

    def initialize_formats_and_rules(self):
        """
        Initializes all text formats based on the current theme and sets up
        the regular expression rules for highlighting.
        """
        formats: Dict[str, QTextCharFormat] = {}
        colors = theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            return QColor(colors.get(f"syntax.{key}", fallback))

        formats["keyword"] = QTextCharFormat()
        formats["keyword"].setForeground(get_color("keyword", "#e67e80"))
        formats["keyword"].setFontWeight(QFont.Weight.Bold)

        formats["self"] = QTextCharFormat()
        formats["self"].setForeground(get_color("self", "#e67e80"))
        formats["self"].setFontItalic(True)

        formats["operator"] = QTextCharFormat()
        formats["operator"].setForeground(get_color("operator", "#d3c6aa"))

        formats["brace"] = QTextCharFormat()
        formats["brace"].setForeground(get_color("brace", "#d3c6aa"))

        formats["decorator"] = QTextCharFormat()
        formats["decorator"].setForeground(get_color("decorator", "#dbbc7f"))
        formats["decorator"].setFontItalic(True)

        formats["className"] = QTextCharFormat()
        formats["className"].setForeground(get_color("className", "#dbbc7f"))
        formats["className"].setFontWeight(QFont.Weight.Bold)

        formats["functionName"] = QTextCharFormat()
        formats["functionName"].setForeground(
            get_color("functionName", "#83c092")
        )

        formats["comment"] = QTextCharFormat()
        formats["comment"].setForeground(get_color("comment", "#5f6c6d"))
        formats["comment"].setFontItalic(True)

        formats["string"] = QTextCharFormat()
        formats["string"].setForeground(get_color("string", "#a7c080"))

        formats["docstring"] = QTextCharFormat()
        formats["docstring"].setForeground(get_color("docstring", "#5f6c6d"))
        formats["docstring"].setFontItalic(True)
        self.multiline_string_format = formats["docstring"]

        formats["number"] = QTextCharFormat()
        formats["number"].setForeground(get_color("number", "#d699b6"))

        self.highlighting_rules = []

        keywords = [
            r'\bdef\b', r'\bclass\b', r'\bif\b', r'\belif\b', r'\belse\b',
            r'\bfor\b', r'\bwhile\b', r'\breturn\b', r'\byield\b', r'\bpass\b',
            r'\bcontinue\b', r'\bbreak\b', r'\bimport\b', r'\bfrom\b',
            r'\bas\b', r'\btry\b', r'\bexcept\b', r'\bfinally\b', r'\braise\b',
            r'\bwith\b', r'\bassert\b', r'\bdel\b', r'\bglobal\b',
            r'\bnonlocal\b', r'\bin\b', r'\bis\b', r'\blambda\b', r'\bnot\b',
            r'\bor\b', r'\band\b', r'\bTrue\b', r'\bFalse\b', r'\bNone\b',
            r'\basync\b', r'\bawait\b'
        ]
        self.highlighting_rules += [
            (QRegularExpression(p), formats["keyword"]) for p in keywords
        ]

        self.highlighting_rules.extend([
            (QRegularExpression(r'\bself\b'), formats["self"]),
            (QRegularExpression(r'@[A-Za-z0-9_]+'), formats["decorator"]),
            (QRegularExpression(r'\b[A-Z][A-Za-z0-9_]*'), formats["className"]),
            (QRegularExpression(r'\b[a-z_][A-Za-z0-9_]*(?=\()'),
             formats["functionName"]),
            (QRegularExpression(r'[+\-*/%=<>!&|^~]'), formats["operator"]),
            (QRegularExpression(r'[{}()\[\]]'), formats["brace"]),
            (QRegularExpression(r'\b[0-9]+\b'), formats["number"]),
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), formats["string"]),
            (QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), formats["string"]),
            (QRegularExpression(r'#.*'), formats["comment"]),
        ])

        self.tri_single_quote_start = QRegularExpression(r"'''")
        self.tri_double_quote_start = QRegularExpression(r'"""')

    def highlightBlock(self, text: str):
        # 1. Apply all single-line rules
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        # 2. Handle multi-line strings with explicit state management
        # State 0: Normal, State 1: In """, State 2: In '''
        NORMAL_STATE = 0
        IN_TRIPLE_DOUBLE = 1
        IN_TRIPLE_SINGLE = 2

        self.setCurrentBlockState(NORMAL_STATE)

        start_index = 0
        previous_state = self.previousBlockState()

        if previous_state == IN_TRIPLE_DOUBLE:
            delimiter = self.tri_double_quote_start
            end_match = delimiter.match(text, 0)
            if end_match.hasMatch():
                length = end_match.capturedEnd()
                self.setFormat(0, length, self.multiline_string_format)
                start_index = length
            else:
                self.setCurrentBlockState(IN_TRIPLE_DOUBLE)
                self.setFormat(0, len(text), self.multiline_string_format)
                return

        elif previous_state == IN_TRIPLE_SINGLE:
            delimiter = self.tri_single_quote_start
            end_match = delimiter.match(text, 0)
            if end_match.hasMatch():
                length = end_match.capturedEnd()
                self.setFormat(0, length, self.multiline_string_format)
                start_index = length
            else:
                self.setCurrentBlockState(IN_TRIPLE_SINGLE)
                self.setFormat(0, len(text), self.multiline_string_format)
                return

        # 3. Find new multi-line strings in the rest of the block
        while start_index < len(text):
            double_match = self.tri_double_quote_start.match(text, start_index)
            single_match = self.tri_single_quote_start.match(text, start_index)

            # Determine which delimiter comes first
            match_to_process, delimiter_re, state_to_set = None, None, None
            if double_match.hasMatch() and (
                    not single_match.hasMatch() or double_match.capturedStart() < single_match.capturedStart()):
                match_to_process = double_match
                delimiter_re = self.tri_double_quote_start
                state_to_set = IN_TRIPLE_DOUBLE
            elif single_match.hasMatch():
                match_to_process = single_match
                delimiter_re = self.tri_single_quote_start
                state_to_set = IN_TRIPLE_SINGLE
            else:
                break  # No more delimiters

            start_pos = match_to_process.capturedStart()
            end_match = delimiter_re.match(text, start_pos + match_to_process.capturedLength())

            if end_match.hasMatch():
                length = end_match.capturedEnd() - start_pos
                self.setFormat(start_pos, length, self.multiline_string_format)
                start_index = end_match.capturedEnd()
            else:
                self.setCurrentBlockState(state_to_set)
                self.setFormat(start_pos, len(text) - start_pos, self.multiline_string_format)
                return

    def rehighlight_document(self):
        """Forces a re-highlight of the entire document."""
        log.info("Re-highlighting entire document for syntax.")
        self.initialize_formats_and_rules()
        super().rehighlight()


class JsonSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for JSON files."""

    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.highlighting_rules = []
        self.initialize_formats_and_rules()
        log.info("JsonSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        """Initializes formats and rules based on the current theme."""
        colors = theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            return QColor(colors.get(f"syntax.{key}", fallback))

        # Format for keys (strings before a colon)
        key_format = QTextCharFormat()
        key_format.setForeground(get_color("className", "#dbbc7f"))

        # Format for string values
        string_format = QTextCharFormat()
        string_format.setForeground(get_color("string", "#a7c080"))

        # Format for numbers
        number_format = QTextCharFormat()
        number_format.setForeground(get_color("number", "#d699b6"))

        # Format for keywords (true, false, null)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(get_color("keyword", "#e67e80"))
        keyword_format.setFontWeight(QFont.Weight.Bold)

        # Format for operators/braces
        brace_format = QTextCharFormat()
        brace_format.setForeground(get_color("brace", "#d3c6aa"))

        # The last rule applied to a character wins, so we apply the general
        # string format first, then overwrite keys with the more specific key format.
        self.highlighting_rules = [
            # Braces and brackets
            (QRegularExpression(r'[\{\}\[\]]'), brace_format),
            # Keywords: true, false, null
            (QRegularExpression(r'\b(true|false|null)\b'), keyword_format),
            # Numbers
            (QRegularExpression(r'\b-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\b'), number_format),
            # All strings get the generic string format first.
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format),
            # Then, re-apply the more specific 'key' format over the top for keys.
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"(?=\s*:)'), key_format),
        ]

    def highlightBlock(self, text: str):
        """Highlights a single block of text."""
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

    def rehighlight_document(self):
        """Forces a re-highlight of the entire document on theme change."""
        self.initialize_formats_and_rules()
        super().rehighlight()


class HtmlSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for HTML code."""

    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.rules = []
        self.multiline_comment_format = QTextCharFormat()
        self.initialize_formats_and_rules()
        log.info("HtmlSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        formats = {}
        colors = theme_manager.current_theme_data.get("colors", {})

        def get_color(key, fallback):
            return QColor(colors.get(f"syntax.{key}", fallback))

        # Format for tags like <p>, <div>
        tag_format = QTextCharFormat()
        tag_format.setForeground(get_color("keyword", "#e67e80"))

        # Format for attributes like href, class
        attribute_format = QTextCharFormat()
        attribute_format.setForeground(get_color("className", "#dbbc7f"))
        attribute_format.setFontItalic(True)

        # Format for attribute values like "styles.css"
        value_format = QTextCharFormat()
        value_format.setForeground(get_color("string", "#a7c080"))

        # Format for HTML comments <!-- ... -->
        comment_format = QTextCharFormat()
        comment_format.setForeground(get_color("comment", "#5f6c6d"))
        comment_format.setFontItalic(True)
        self.multiline_comment_format = comment_format

        # Format for DOCTYPE
        doctype_format = QTextCharFormat()
        doctype_format.setForeground(get_color("decorator", "#dbbc7f"))

        self.rules = [
            # Tags: <tag>, </tag>, <tag/>
            (QRegularExpression(r"</?([a-zA-Z0-9_-]+)"), tag_format),
            # Attributes: href=, class=
            (QRegularExpression(r'\b([a-zA-Z_-]+)(?=\s*=)'), attribute_format),
            # Attribute values in quotes
            (QRegularExpression(r'"[^"]*"'), value_format),
            (QRegularExpression(r"'[^']*'"), value_format),
            # DOCTYPE
            (QRegularExpression(r'<!DOCTYPE[^>]*>'), doctype_format),
        ]

        self.comment_start_expression = QRegularExpression(r"<!--")
        self.comment_end_expression = QRegularExpression(r"-->")

    def highlightBlock(self, text: str):
        # Apply single-line rules first
        for pattern, fmt in self.rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        self.setCurrentBlockState(0)

        in_multiline_comment = self.previousBlockState() == 1
        start_index = 0

        if in_multiline_comment:
            end_match = self.comment_end_expression.match(text, 0)
            if end_match.hasMatch():
                length = end_match.capturedEnd()
                self.setFormat(0, length, self.multiline_comment_format)
                start_index = length
            else:
                self.setCurrentBlockState(1)
                self.setFormat(0, len(text), self.multiline_comment_format)
                return

        search_index = start_index
        while search_index >= 0 and search_index < len(text):
            start_match = self.comment_start_expression.match(text, search_index)
            if not start_match.hasMatch():
                break

            start_pos = start_match.capturedStart()
            end_match = self.comment_end_expression.match(text, start_pos + start_match.capturedLength())
            if end_match.hasMatch():
                length = end_match.capturedEnd() - start_pos
                self.setFormat(start_pos, length, self.multiline_comment_format)
                search_index = end_match.capturedEnd()
            else:
                self.setCurrentBlockState(1)
                self.setFormat(start_pos, len(text) - start_pos, self.multiline_comment_format)
                return

    def rehighlight_document(self):
        self.initialize_formats_and_rules()
        super().rehighlight()


class CppSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for C and C++ code."""

    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_comment_format = QTextCharFormat()

        self.initialize_formats_and_rules()
        log.info("CppSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        """Initializes all text formats and regular expression rules."""
        formats: Dict[str, QTextCharFormat] = {}
        colors = theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            # Re-use existing python syntax colors for simplicity and consistency
            return QColor(colors.get(f"syntax.{key}", fallback))

        formats["keyword"] = QTextCharFormat()
        formats["keyword"].setForeground(get_color("keyword", "#e67e80"))
        formats["keyword"].setFontWeight(QFont.Weight.Bold)

        formats["preprocessor"] = QTextCharFormat()
        formats["preprocessor"].setForeground(get_color("decorator", "#dbbc7f"))
        formats["preprocessor"].setFontWeight(QFont.Weight.Medium)

        formats["operator"] = QTextCharFormat()
        formats["operator"].setForeground(get_color("operator", "#d3c6aa"))

        formats["brace"] = QTextCharFormat()
        formats["brace"].setForeground(get_color("brace", "d3c6aa"))

        formats["className"] = QTextCharFormat()
        formats["className"].setForeground(get_color("className", "#dbbc7f"))

        formats["functionName"] = QTextCharFormat()
        formats["functionName"].setForeground(get_color("functionName", "#83c092"))

        formats["comment"] = QTextCharFormat()
        formats["comment"].setForeground(get_color("comment", "#5f6c6d"))
        formats["comment"].setFontItalic(True)
        self.multiline_comment_format = formats["comment"]

        formats["string"] = QTextCharFormat()
        formats["string"].setForeground(get_color("string", "#a7c080"))

        formats["number"] = QTextCharFormat()
        formats["number"].setForeground(get_color("number", "#d699b6"))

        # Build Rule List
        self.highlighting_rules = []

        keywords = [
            r'\bchar\b', r'\bclass\b', r'\bconst\b', r'\bdouble\b', r'\benum\b',
            r'\bexplicit\b', r'\bfloat\b', r'\bfriend\b', r'\binline\b',
            r'\bint\b', r'\blong\b', r'\bnamespace\b', r'\boperator\b',
            r'\bprivate\b', r'\bprotected\b', r'\bpublic\b', r'\bshort\b',
            r'\bsigned\b', r'\bstatic\b', r'\bstruct\b', r'\btemplate\b',
            r'\btypedef\b', r'\btypename\b', r'\bunion\b', r'\bunsigned\b',
            r'\bvirtual\b', r'\bvoid\b', r'\bvolatile\b', r'\bwchar_t\b',
            # Control flow
            r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b', r'\bdo\b',
            r'\bbreak\b', r'\bcontinue\b', r'\breturn\b', r'\bgoto\b',
            r'\bswitch\b', r'\bcase\b', r'\bdefault\b',
            # C++ specific
            r'\bnew\b', r'\bdelete\b', r'\bthis\b', r'\bthrow\b', r'\btry\b',
            r'\bcatch\b', r'\bexplicit\b', r'\bexport\b', r'\btrue\b',
            r'\bfalse\b', r'\bnullptr\b', r'\busing\b',
            # Newer keywords
            r'\bnoexcept\b', r'\bstatic_assert\b', r'\bdecltype\b', r'\bauto\b'
        ]
        self.highlighting_rules += [(QRegularExpression(p), formats["keyword"]) for p in keywords]

        self.highlighting_rules.extend([
            (QRegularExpression(r'^\s*#.*'), formats["preprocessor"]),
            (QRegularExpression(r'\b[A-Z][A-Za-z0-9_]*'), formats["className"]),
            (QRegularExpression(r'\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()'), formats["functionName"]),
            (QRegularExpression(r'[=><!~?&|+\-*/^%:]+'), formats["operator"]),
            (QRegularExpression(r'\{|\}|\(|\)|\[|\]'), formats["brace"]),
            (QRegularExpression(r'\b[0-9]+[fLu]?\b'), formats["number"]),
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), formats["string"]),
            (QRegularExpression(r"'\\?.'"), formats["string"]),  # Char literal
            (QRegularExpression(r'//.*'), formats["comment"]),
        ])

        self.comment_start_expression = QRegularExpression(r"/\*")
        self.comment_end_expression = QRegularExpression(r"\*/")

    def highlightBlock(self, text: str):
        # Apply single-line rules first
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        self.setCurrentBlockState(0)

        in_multiline_comment = self.previousBlockState() == 1
        start_index = 0

        if in_multiline_comment:
            end_match = self.comment_end_expression.match(text, 0)
            if end_match.hasMatch():
                length = end_match.capturedEnd()
                self.setFormat(0, length, self.multiline_comment_format)
                start_index = length
            else:
                self.setCurrentBlockState(1)
                self.setFormat(0, len(text), self.multiline_comment_format)
                return

        search_index = start_index
        while search_index >= 0 and search_index < len(text):
            start_match = self.comment_start_expression.match(text, search_index)
            if not start_match.hasMatch():
                break

            start_pos = start_match.capturedStart()
            end_match = self.comment_end_expression.match(text, start_pos + start_match.capturedLength())
            if end_match.hasMatch():
                length = end_match.capturedEnd() - start_pos
                self.setFormat(start_pos, length, self.multiline_comment_format)
                search_index = end_match.capturedEnd()
            else:
                self.setCurrentBlockState(1)
                self.setFormat(start_pos, len(text) - start_pos, self.multiline_comment_format)
                return

    def rehighlight_document(self):
        """Forces a re-highlight of the entire document, usually on theme change."""
        self.initialize_formats_and_rules()
        super().rehighlight()


class CSharpSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for C# code."""

    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_comment_format = QTextCharFormat()
        self.initialize_formats_and_rules()
        log.info("CSharpSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        formats = {}
        colors = theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            return QColor(colors.get(f"syntax.{key}", fallback))

        formats["keyword"] = QTextCharFormat()
        formats["keyword"].setForeground(get_color("keyword", "#e67e80"))
        formats["keyword"].setFontWeight(QFont.Weight.Bold)

        formats["preprocessor"] = QTextCharFormat()
        formats["preprocessor"].setForeground(get_color("decorator", "#dbbc7f"))

        formats["string"] = QTextCharFormat()
        formats["string"].setForeground(get_color("string", "#a7c080"))

        formats["comment"] = QTextCharFormat()
        formats["comment"].setForeground(get_color("comment", "#5f6c6d"))
        formats["comment"].setFontItalic(True)
        self.multiline_comment_format = formats["comment"]

        formats["number"] = QTextCharFormat()
        formats["number"].setForeground(get_color("number", "#d699b6"))

        formats["className"] = QTextCharFormat()
        formats["className"].setForeground(get_color("className", "#dbbc7f"))

        formats["functionName"] = QTextCharFormat()
        formats["functionName"].setForeground(get_color("functionName", "#83c092"))

        # Rule construction
        self.highlighting_rules = []

        keywords = [
            r'\babstract\b', r'\bas\b', r'\bbase\b', r'\bbool\b', r'\bbreak\b',
            r'\bbyte\b', r'\bcase\b', r'\bcatch\b', r'\bchar\b', r'\bchecked\b',
            r'\bclass\b', r'\bconst\b', r'\bcontinue\b', r'\bdecimal\b',
            r'\bdefault\b', r'\bdelegate\b', r'\bdo\b', r'\bdouble\b', r'\belse\b',
            r'\benum\b', r'\bevent\b', r'\bexplicit\b', r'\bextern\b', r'\bfalse\b',
            r'\bfinally\b', r'\bfixed\b', r'\bfloat\b', r'\bfor\b', r'\bforeach\b',
            r'\bgoto\b', r'\bif\b', r'\bimplicit\b', r'\bin\b', r'\bint\b',
            r'\binterface\b', r'\binternal\b', r'\bis\b', r'\block\b', r'\blong\b',
            r'\bnamespace\b', r'\bnew\b', r'\bnull\b', r'\bobject\b',
            r'\boperator\b', r'\bout\b', r'\boverride\b', r'\bparams\b',
            r'\bprivate\b', r'\bprotected\b', r'\bpublic\b', r'\breadonly\b',
            r'\bref\b', r'\breturn\b', r'\bsbyte\b', r'\bsealed\b', r'\bshort\b',
            r'\bsizeof\b', r'\bstackalloc\b', r'\bstatic\b', r'\bstring\b',
            r'\bstruct\b', r'\bswitch\b', r'\bthis\b', r'\bthrow\b', r'\btrue\b',
            r'\btry\b', r'\btypeof\b', r'\buint\b', r'\bulong\b', r'\bunchecked\b',
            r'\bunsafe\b', r'\bushort\b', r'\busing\b', r'\bvirtual\b',
            r'\bvoid\b', r'\bvolatile\b', r'\bwhile\b', r'\byield\b', r'\bvar\b'
        ]

        self.highlighting_rules += [(QRegularExpression(p), formats["keyword"]) for p in keywords]

        self.highlighting_rules.extend([
            (QRegularExpression(r'^\s*#[a-zA-Z_]+'), formats["preprocessor"]),
            (QRegularExpression(r'\b[A-Z][A-Za-z0-9_]*'), formats["className"]),
            (QRegularExpression(r'\b[A-Z][a-zA-Z0-9_]*(?=\s*\()'), formats["functionName"]),
            (QRegularExpression(r'"(?:[^"\\]|\\.)*"'), formats["string"]),
            (QRegularExpression(r"'\\?.'"), formats["string"]),
            (QRegularExpression(r'//.*'), formats["comment"]),
        ])

        self.comment_start_expression = QRegularExpression(r"/\*")
        self.comment_end_expression = QRegularExpression(r"\*/")

    def highlightBlock(self, text: str):
        # Apply single-line rules first
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        self.setCurrentBlockState(0)

        in_multiline_comment = self.previousBlockState() == 1
        start_index = 0

        if in_multiline_comment:
            end_match = self.comment_end_expression.match(text, 0)
            if end_match.hasMatch():
                length = end_match.capturedEnd()
                self.setFormat(0, length, self.multiline_comment_format)
                start_index = length
            else:
                self.setCurrentBlockState(1)
                self.setFormat(0, len(text), self.multiline_comment_format)
                return

        search_index = start_index
        while search_index >= 0 and search_index < len(text):
            start_match = self.comment_start_expression.match(text, search_index)
            if not start_match.hasMatch():
                break

            start_pos = start_match.capturedStart()
            end_match = self.comment_end_expression.match(text, start_pos + start_match.capturedLength())
            if end_match.hasMatch():
                length = end_match.capturedEnd() - start_pos
                self.setFormat(start_pos, length, self.multiline_comment_format)
                search_index = end_match.capturedEnd()
            else:
                self.setCurrentBlockState(1)
                self.setFormat(start_pos, len(text) - start_pos, self.multiline_comment_format)
                return

    def rehighlight_document(self):
        self.initialize_formats_and_rules()
        super().rehighlight()


class JavaScriptSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for JavaScript code."""

    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_comment_format = QTextCharFormat()

        self.initialize_formats_and_rules()
        log.info("JavaScriptSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        """Initializes all text formats based on the current theme and sets up regex rules."""
        self.formats: Dict[str, QTextCharFormat] = {}
        colors = theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            # Re-use existing python syntax colors for simplicity
            return QColor(colors.get(f"syntax.{key}", fallback))

        self.formats["keyword"] = QTextCharFormat()
        self.formats["keyword"].setForeground(get_color("keyword", "#e67e80"))
        self.formats["keyword"].setFontWeight(QFont.Weight.Bold)

        self.formats["operator"] = QTextCharFormat()
        self.formats["operator"].setForeground(get_color("operator", "#d3c6aa"))

        self.formats["brace"] = QTextCharFormat()
        self.formats["brace"].setForeground(get_color("brace", "d3c6aa"))

        self.formats["className"] = QTextCharFormat()
        self.formats["className"].setForeground(get_color("className", "#dbbc7f"))
        self.formats["className"].setFontWeight(QFont.Weight.Bold)

        self.formats["functionName"] = QTextCharFormat()
        self.formats["functionName"].setForeground(get_color("functionName", "#83c092"))

        self.formats["comment"] = QTextCharFormat()
        self.formats["comment"].setForeground(get_color("comment", "#5f6c6d"))
        self.formats["comment"].setFontItalic(True)
        self.multiline_comment_format = self.formats["comment"]

        self.formats["string"] = QTextCharFormat()
        self.formats["string"].setForeground(get_color("string", "#a7c080"))

        self.formats["number"] = QTextCharFormat()
        self.formats["number"].setForeground(get_color("number", "#d699b6"))

        # Build Rule List
        self.highlighting_rules = []

        keywords = [
            r'\bfunction\b', r'\bclass\b', r'\blet\b', r'\bconst\b', r'\bvar\b',
            r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b', r'\breturn\b',
            r'\bswitch\b', r'\bcase\b', r'\bdefault\b', r'\bnew\b', r'\bthis\b',
            r'\btry\b', r'\bcatch\b', r'\bfinally\b', r'\bthrow\b', r'\btypeof\b',
            r'\bimport\b', r'\bexport\b', r'\bfrom\b', r'\basync\b', r'\bawait\b',
            r'\btrue\b', r'\bfalse\b', r'\bnull\b', r'\bundefined\b'
        ]
        self.highlighting_rules += [(QRegularExpression(p), self.formats["keyword"]) for p in keywords]

        self.highlighting_rules.extend([
            (QRegularExpression(r'\b[A-Z][A-Za-z0-9_]*'), self.formats["className"]),
            (QRegularExpression(r'[a-z_][A-Za-z0-9_]*(?=\s*=\s*function|\s*=\s*\(|\s*\()'), self.formats["functionName"]),
            (QRegularExpression(r'[=><!~?&|+\-*/^%]+'), self.formats["operator"]),
            (QRegularExpression(r'\{|\}|\(|\)|\[|\]'), self.formats["brace"]),
            (QRegularExpression(r'\b[0-9]+(\.[0-9]+)?\b'), self.formats["number"]),
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.formats["string"]),
            (QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), self.formats["string"]),
            (QRegularExpression(r"`[^`\\]*(\\.[^`\\]*)*`"), self.formats["string"]),  # Template literals
            (QRegularExpression(r'//.*'), self.formats["comment"]),
        ])

        # For multiline comments /* ... */
        self.comment_start_expression = QRegularExpression(r"/\*")
        self.comment_end_expression = QRegularExpression(r"\*/")

    def highlightBlock(self, text: str):
        # Apply single-line rules first
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        self.setCurrentBlockState(0)

        in_multiline_comment = self.previousBlockState() == 1
        start_index = 0

        if in_multiline_comment:
            end_match = self.comment_end_expression.match(text, 0)
            if end_match.hasMatch():
                length = end_match.capturedEnd()
                self.setFormat(0, length, self.multiline_comment_format)
                start_index = length
            else:
                self.setCurrentBlockState(1)
                self.setFormat(0, len(text), self.multiline_comment_format)
                return

        search_index = start_index
        while search_index >= 0 and search_index < len(text):
            start_match = self.comment_start_expression.match(text, search_index)
            if not start_match.hasMatch():
                break

            start_pos = start_match.capturedStart()
            end_match = self.comment_end_expression.match(text, start_pos + start_match.capturedLength())
            if end_match.hasMatch():
                length = end_match.capturedEnd() - start_pos
                self.setFormat(start_pos, length, self.multiline_comment_format)
                search_index = end_match.capturedEnd()
            else:
                self.setCurrentBlockState(1)
                self.setFormat(start_pos, len(text) - start_pos, self.multiline_comment_format)
                return

    def rehighlight_document(self):
        """Forces a re-highlight of the entire document, usually on theme change."""
        self.initialize_formats_and_rules()
        super().rehighlight()


class RustSyntaxHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for Rust code."""

    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.highlighting_rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self.multiline_comment_format = QTextCharFormat()
        self.initialize_formats_and_rules()
        log.info("RustSyntaxHighlighter initialized.")

    def initialize_formats_and_rules(self):
        """Initializes all text formats and regular expression rules based on the theme."""
        self.formats: Dict[str, QTextCharFormat] = {}
        colors = theme_manager.current_theme_data.get("colors", {})

        def get_color(key: str, fallback: str) -> QColor:
            return QColor(colors.get(f"syntax.{key}", fallback))

        self.formats["keyword"] = QTextCharFormat()
        self.formats["keyword"].setForeground(get_color("keyword", "#e67e80"))
        self.formats["keyword"].setFontWeight(QFont.Weight.Bold)

        self.formats["special"] = QTextCharFormat()
        self.formats["special"].setForeground(get_color("self", "#e67e80"))
        self.formats["special"].setFontItalic(True)

        self.formats["attribute"] = QTextCharFormat()
        self.formats["attribute"].setForeground(get_color("decorator", "#dbbc7f"))

        self.formats["macro"] = QTextCharFormat()
        self.formats["macro"].setForeground(get_color("decorator", "#dbbc7f"))

        self.formats["type"] = QTextCharFormat()
        self.formats["type"].setForeground(get_color("className", "#dbbc7f"))

        self.formats["functionName"] = QTextCharFormat()
        self.formats["functionName"].setForeground(get_color("functionName", "#83c092"))

        self.formats["comment"] = QTextCharFormat()
        self.formats["comment"].setForeground(get_color("comment", "#5f6c6d"))
        self.formats["comment"].setFontItalic(True)
        self.multiline_comment_format = self.formats["comment"]

        self.formats["string"] = QTextCharFormat()
        self.formats["string"].setForeground(get_color("string", "#a7c080"))

        self.formats["number"] = QTextCharFormat()
        self.formats["number"].setForeground(get_color("number", "#d699b6"))

        self.highlighting_rules = []
        keywords = [
            r'\b(as|break|const|continue|crate|else|enum|extern|false|fn|for|if|impl|in|let|loop|match|mod|move|mut|pub|ref|return|static|struct|super|trait|true|type|unsafe|use|where|while|async|await|dyn)\b'
        ]
        self.highlighting_rules += [(QRegularExpression(p), self.formats["keyword"]) for p in keywords]
        special_keywords = [r'\b(self|Self)\b']
        self.highlighting_rules += [(QRegularExpression(p), self.formats["special"]) for p in special_keywords]
        self.highlighting_rules.extend([
            (QRegularExpression(r"#\!\[[^\]]+\]|#\[[^\]]+\]"), self.formats["attribute"]),
            (QRegularExpression(r"\b([a-zA-Z0-9_]+)!\b"), self.formats["macro"]),
            (QRegularExpression(r'\b[A-Z][a-zA-Z0-9_]*\b'), self.formats["type"]),
            (QRegularExpression(r'\b(fn)\s+([a-zA-Z_][a-zA-Z0-9_]*)'), self._format_function_definition),
            (QRegularExpression(r"'\w+"), self.formats["special"]),
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.formats["string"]),
            (QRegularExpression(r'\b[0-9]+(_[0-9]+)*\.?[0-9]*\b'), self.formats["number"]),
            (QRegularExpression(r'//.*'), self.formats["comment"]),
        ])
        self.comment_start_expression = QRegularExpression(r"/\*")
        self.comment_end_expression = QRegularExpression(r"\*/")

    def _format_function_definition(self, match):
        """Custom formatter to style `fn` as keyword and name as functionName."""
        self.setFormat(match.capturedStart(1), match.capturedLength(1), self.formats["keyword"])
        self.setFormat(match.capturedStart(2), match.capturedLength(2), self.formats["functionName"])

    def highlightBlock(self, text: str):
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                if callable(fmt):
                    fmt(match)
                else:
                    self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
        self.setCurrentBlockState(0)
        in_multiline_comment = self.previousBlockState() == 1
        start_index = 0
        if in_multiline_comment:
            end_match = self.comment_end_expression.match(text, 0)
            if end_match.hasMatch():
                length = end_match.capturedEnd()
                self.setFormat(0, length, self.multiline_comment_format)
                start_index = length
            else:
                self.setCurrentBlockState(1)
                self.setFormat(0, len(text), self.multiline_comment_format)
                return
        search_index = start_index
        while search_index >= 0 and search_index < len(text):
            start_match = self.comment_start_expression.match(text, search_index)
            if not start_match.hasMatch():
                break
            start_pos = start_match.capturedStart()
            end_match = self.comment_end_expression.match(text, start_pos + start_match.capturedLength())
            if end_match.hasMatch():
                length = end_match.capturedEnd() - start_pos
                self.setFormat(start_pos, length, self.multiline_comment_format)
                search_index = end_match.capturedEnd()
            else:
                self.setCurrentBlockState(1)
                self.setFormat(start_pos, len(text) - start_pos, self.multiline_comment_format)
                return

    def rehighlight_document(self):
        self.initialize_formats_and_rules()
        super().rehighlight()