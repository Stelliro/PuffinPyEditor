# Project Export: PuffinPyEditor
## Export Timestamp: 2025-07-05T20:39:25.363849
---

## Golden Rules
1. Only edit and add features, the only features should stay unless asked to be removed, or may be completely redundant.
2. any scripts over 1000 lines, please write in a new response.
3. multiple scripts together exceeding 2000 lines together need to be separated into smaller responses, (example: these scripts have 2340 lines together I'm going to separate it into 2 messages that way i dont lose formatting and dont accidentally remove any features)
4. Do not remove any code that is unrelated to the fix, only remove code if it is being substituted or is not needed anymore.

---

## Project Files

Here is the project context you need to work with.
## File Tree
```
/PuffinPyEditor
 ├── app_core
 │   └── syntax_highlighters.py
 └── plugins
     └── script_runner
         ├── code_runner.py
         ├── output_panel.py
         ├── plugin.json
         └── plugin_main.py

```
## File Contents
### File: `/app_core/syntax_highlighters.py`

```python
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
```

### File: `/plugins/script_runner/code_runner.py`

```python
# PuffinPyEditor/plugins/pythong_tools/code_runner.py
import os
import sys
import shutil
from PyQt6.QtCore import QObject, pyqtSignal, QProcess
from app_core.settings_manager import settings_manager
from utils.logger import log
from typing import Optional


def _find_python_interpreter() -> str:
    """
    Intelligently finds the best Python executable for running scripts.
    This prevents the app from trying to execute itself when frozen.

    Priority:
    1. User-defined path in settings.
    2. A 'python.exe' bundled alongside the main PuffinPyEditor.exe.
    3. The python.exe from the current virtual environment (if from source).
    4. The first 'python' found on the system's PATH.

    Returns:
        The path to a suitable Python executable, or an empty string.
    """
    # 1. User-defined path
    user_path = settings_manager.get("python_interpreter_path", "").strip()
    if user_path and os.path.exists(user_path) and \
            "PuffinPyEditor.exe" not in user_path:
        log.info(f"CodeRunner: Using user-defined interpreter: {user_path}")
        return user_path

    # 2. Local python.exe if frozen (e.g., if bundled with the app)
    if getattr(sys, 'frozen', False):
        local_python_path = os.path.join(os.path.dirname(sys.executable), "python.exe")
        if os.path.exists(local_python_path):
            log.info("CodeRunner: Found local python.exe in frozen app dir: "
                     f"{local_python_path}")
            return local_python_path

    # 3. Venv python if running from source
    if not getattr(sys, 'frozen', False):
        # Ensure we don't return the main app if it was launched via a script
        if "PuffinPyEditor.exe" not in sys.executable:
            log.info("CodeRunner: Running from source, using sys.executable: "
                     f"{sys.executable}")
            return sys.executable

    # 4. System PATH python
    system_python = shutil.which("python")
    if system_python and "PuffinPyEditor.exe" not in system_python:
        log.info(f"CodeRunner: Found system python on PATH: {system_python}")
        return system_python

    log.error("CodeRunner: Could not find a suitable Python interpreter.")
    return ""


class CodeRunner(QObject):
    """
    Manages the execution of Python scripts in a separate process.
    """
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    process_finished = pyqtSignal(int)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.process: Optional[QProcess] = None

    def run_script(self, script_filepath: str):
        """
        Executes a Python script using the configured interpreter.

        Args:
            script_filepath: The absolute path to the Python script to run.
        """
        if not script_filepath or not os.path.exists(script_filepath):
            err_msg = f"Script path is invalid: {script_filepath}"
            log.error(err_msg)
            self.error_received.emit(err_msg + "\n")
            self.process_finished.emit(-1)
            return

        interpreter_path = _find_python_interpreter()

        if not interpreter_path:
            err_msg = ("Could not find a valid Python interpreter.\nPlease set "
                       "a path in Preferences or ensure 'python' is in your "
                       "system PATH.")
            log.error(err_msg)
            self.error_received.emit(err_msg + "\n")
            self.process_finished.emit(-1)
            return

        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            warning_msg = "A script is already running. Please wait."
            log.warning(warning_msg)
            self.error_received.emit(f"[INFO] {warning_msg}\n")
            return

        self.process = QProcess()
        self.process.setProgram(interpreter_path)
        self.process.setArguments([script_filepath])

        # Set working dir to script's dir for correct relative imports
        script_dir = os.path.dirname(script_filepath)
        self.process.setWorkingDirectory(script_dir)
        log.info(f"Setting working directory for script to: {script_dir}")

        # Connect signals
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        self.process.errorOccurred.connect(self._handle_process_error)

        log.info(f"Starting script: '{interpreter_path}' '{script_filepath}'")
        self.output_received.emit(
            f"[PuffinPyRun] Executing: {os.path.basename(script_filepath)} ...\n")
        self.process.start()

        if not self.process.waitForStarted(5000):
            err_msg = f"Failed to start process: {self.process.errorString()}"
            log.error(err_msg)
            self.error_received.emit(err_msg + "\n")
            self.process_finished.emit(self.process.exitCode())
            self.process = None  # Clean up the failed process
            return

        pid = self.process.processId() if self.process else 'N/A'
        log.debug(f"Process started successfully (PID: {pid}).")

    def stop_script(self):
        """Terminates the currently running script process."""
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            pid = self.process.processId()
            log.info(f"Attempting to terminate process (PID: {pid}).")
            self.output_received.emit("[PuffinPyRun] Terminating script...\n")
            self.process.terminate()
            # If terminate fails, forcefully kill it
            if not self.process.waitForFinished(1000):
                log.warning(f"Process {pid} did not terminate gracefully, killing.")
                self.process.kill()
                self.output_received.emit("[PuffinPyRun] Script process killed.\n")
            else:
                self.output_received.emit("[PuffinPyRun] Script process terminated.\n")
        else:
            log.info("Stop script requested, but no process is running.")

    def _handle_stdout(self):
        if self.process:
            data = self.process.readAllStandardOutput().data().decode(errors='replace')
            self.output_received.emit(data)

    def _handle_stderr(self):
        if self.process:
            data = self.process.readAllStandardError().data().decode(errors='replace')
            self.error_received.emit(data)

    def _handle_finished(self, exit_code: int, exit_status: QProcess.ExitStatus):
        log.info(f"Script finished. Exit code: {exit_code}, Status: {exit_status.name}")
        if exit_status == QProcess.ExitStatus.CrashExit:
            self.error_received.emit("[PuffinPyRun] Script process crashed.\n")

        self.output_received.emit(
            f"[PuffinPyRun] Process finished with exit code {exit_code}.\n")
        self.process_finished.emit(exit_code)
        self.process = None  # Clean up after finishing

    def _handle_process_error(self, error: QProcess.ProcessError):
        if self.process:
            err_msg = f"[PuffinPyRun] QProcess Error: {self.process.errorString()} " \
                      f"(Code: {error.name})"
            log.error(err_msg)
            self.error_received.emit(err_msg + "\n")
```

### File: `/plugins/script_runner/output_panel.py`

```python
# PuffinPyEditor/plugins/pythong_tools/output_panel.py
from PyQt6.QtWidgets import QDockWidget, QTextEdit, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from app_core.settings_manager import settings_manager
from app_core.theme_manager import theme_manager


class OutputPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Output", parent)
        self.setObjectName("OutputPanelDock")
        self.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea |
                             Qt.DockWidgetArea.RightDockWidgetArea)

        self.container_widget = QWidget()
        self.layout = QVBoxLayout(self.container_widget)
        self.layout.setContentsMargins(2, 2, 2, 2)

        self.control_bar_layout = QHBoxLayout()
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_output)
        self.control_bar_layout.addWidget(self.clear_button)
        self.control_bar_layout.addStretch(1)
        self.layout.addLayout(self.control_bar_layout)

        self.output_text_edit = QTextEdit()
        self.output_text_edit.setReadOnly(True)
        self.layout.addWidget(self.output_text_edit)

        self.container_widget.setLayout(self.layout)
        self.setWidget(self.container_widget)

        self.update_theme()

    def append_output(self, text: str, is_error: bool = False):
        original_text_color = self.output_text_edit.textColor()
        if is_error:
            colors = theme_manager.current_theme_data.get("colors", {})
            error_color_hex = colors.get("syntax.comment", "#FF4444")
            error_color = QColor(error_color_hex if error_color_hex else "#FF0000")
            self.output_text_edit.setTextColor(error_color)

        self.output_text_edit.append(text.strip())
        if is_error:
            self.output_text_edit.setTextColor(original_text_color)
        scrollbar = self.output_text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_output(self):
        self.output_text_edit.clear()

    def update_theme(self):
        font_family = settings_manager.get("font_family", "Consolas")
        font_size = settings_manager.get("font_size", 10)
        font = QFont(font_family, font_size)
        self.output_text_edit.setFont(font)

        colors = theme_manager.current_theme_data.get("colors", {})
        bg_color = colors.get("editor.background", "#1e1e1e")
        fg_color = colors.get("editor.foreground", "#d4d4d4")
        self.output_text_edit.setStyleSheet(f"background-color: {bg_color}; "
                                              f"color: {fg_color}; border: none;")
```

### File: `/plugins/script_runner/plugin.json`

```json
{
    "id": "script_runner",
    "name": "Script Runner",
    "author": "PuffinPy Team",
    "version": "1.2.0",
    "description": "Adds functionality to run Python, C++, C#, and JavaScript files from the editor.",
    "entry_point": "plugin_main.py"
}
```

### File: `/plugins/script_runner/plugin_main.py`

```python
# PuffinPyEditor/plugins/script_runner/plugin_main.py
import os
import sys
import shutil
import platform
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, QProcess, QTimer
from app_core.puffin_api import PuffinPluginAPI
from .output_panel import OutputPanel
from .code_runner import CodeRunner, _find_python_interpreter
from utils.logger import log


class ScriptRunnerPlugin(QObject):
    def __init__(self, puffin_api: PuffinPluginAPI):
        super().__init__()
        self.api = puffin_api
        self.main_window = self.api.get_main_window()
        self.output_panel = OutputPanel(self.main_window)
        self.process = None
        self._current_task_info = {}

        self.RUN_CONFIG = {
            '.py': {'handler': self._run_python_script, 'menu_text': 'Run Python Script', 'shortcut': 'F5',
                    'icon': 'mdi.language-python'},
            '.js': {'handler': self._run_node_script, 'menu_text': 'Run JS File', 'shortcut': 'Ctrl+F5',
                    'icon': 'mdi.language-javascript'},
            '.cpp': {'handler': self._compile_run_cpp, 'menu_text': 'Compile & Run C++', 'shortcut': 'F6',
                     'icon': 'mdi.language-cpp'},
            '.c': {'handler': self._compile_run_cpp, 'menu_text': 'Compile & Run C', 'shortcut': 'F6',
                   'icon': 'mdi.language-cpp'},
            '.cs': {'handler': self._compile_run_csharp, 'menu_text': 'Compile & Run C#', 'shortcut': 'F7',
                    'icon': 'mdi.language-csharp'},
        }
        self.run_actions = {}
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.api.add_dock_panel(
            widget=self.output_panel,
            title="Output",
            area_str="bottom",
            icon_name='mdi.console-line'
        )
        for config in self.RUN_CONFIG.values():
            action = self.api.add_menu_action("run", config['menu_text'], config['handler'], config['shortcut'],
                                              config['icon'])
            action.setEnabled(False)
            self.run_actions[config['menu_text']] = action

        self.stop_action = self.api.add_menu_action("run", "Stop Script", self.stop_script, "Ctrl+F2",
                                                    'mdi.stop-circle-outline')
        self.stop_action.setEnabled(False)

        # Add only the Python run/stop actions to the main toolbar for prominence
        py_action = self.run_actions['Run Python Script']
        self.api.add_toolbar_action(py_action)
        self.api.add_toolbar_action(self.stop_action)

    def _connect_signals(self):
        self.main_window.tab_widget.currentChanged.connect(self._on_tab_changed)
        QTimer.singleShot(0, lambda: self._on_tab_changed(self.main_window.tab_widget.currentIndex()))
        self.main_window.theme_changed_signal.connect(self.output_panel.update_theme)

    def _on_tab_changed(self, index):
        from ui.editor_widget import EditorWidget
        active_ext = None
        if index != -1:
            if widget := self.main_window.tab_widget.widget(index):
                if isinstance(widget, EditorWidget):
                    if data := self.main_window.editor_tabs_data.get(widget):
                        if filepath := data.get('filepath'):
                            _, active_ext = os.path.splitext(filepath)

        for ext, config in self.RUN_CONFIG.items():
            action = self.run_actions.get(config['menu_text'])
            if action:
                action.setEnabled(ext == active_ext)

    def stop_script(self):
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.output_panel.append_output("[Runner] Terminating process...\n", is_error=True)
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                self.process.kill()
                self.output_panel.append_output("[Runner] Process killed.\n", is_error=True)
        else:
            self._on_run_finished(-1)

    def _get_current_filepath(self):
        from ui.editor_widget import EditorWidget
        editor = self.main_window.tab_widget.currentWidget()
        if not isinstance(editor, EditorWidget):
            return None

        filepath = self.main_window.editor_tabs_data.get(editor, {}).get('filepath')
        if not filepath:
            self.api.show_message("info", "Save File", "Please save the file before running.")
            return None

        if self.main_window._is_editor_modified(editor):
            self.main_window._action_save_file()

        return filepath

    def _run_python_script(self):
        if not (filepath := self._get_current_filepath()): return
        if not (interpreter_path := _find_python_interpreter()):
            self.api.show_message("critical", "Python Not Found", "Could not find a Python interpreter.")
            return

        self._current_task_info = {'name': 'Python Script'}
        self._start_process(interpreter_path, [filepath])

    def _run_node_script(self):
        if not (filepath := self._get_current_filepath()): return
        if not (node_path := shutil.which("node")):
            self.api.show_message("critical", "Node.js Not Found", "Could not find 'node' on your system PATH.")
            return

        self._current_task_info = {'name': 'Node.js Script'}
        self._start_process(node_path, [filepath])

    def _compile_run_cpp(self):
        if not (source_path := self._get_current_filepath()): return
        compiler_path = shutil.which("g++") or shutil.which("cl")
        if not compiler_path:
            self.api.show_message("critical", "Compiler Not Found", "No C++ compiler (g++ or cl.exe) found.")
            return

        source_dir = os.path.dirname(source_path)
        base_name = os.path.splitext(os.path.basename(source_path))[0]
        exe_path = os.path.join(source_dir, base_name + (".exe" if platform.system() == "Windows" else ""))

        if "g++" in os.path.basename(compiler_path):
            args = [source_path, "-o", exe_path, "-std=c++17", "-Wall"]
        else:  # cl.exe
            args = [source_path, f"/Fe:{exe_path}", "/EHsc"]

        self._current_task_info = {'name': 'C++ Compilation', 'type': 'compile', 'runner_path': exe_path}
        self._start_process(compiler_path, args)

    def _compile_run_csharp(self):
        if not (source_path := self._get_current_filepath()): return
        if not (compiler_path := shutil.which("csc")):
            self.api.show_message("critical", "C# Compiler Not Found", "C# compiler (csc.exe) not found.")
            return

        source_dir = os.path.dirname(source_path)
        base_name = os.path.splitext(os.path.basename(source_path))[0]
        exe_path = os.path.join(source_dir, f"{base_name}.exe")

        args = [f"/out:{exe_path}", source_path]
        self._current_task_info = {'name': 'C# Compilation', 'type': 'compile', 'runner_path': exe_path}
        self._start_process(compiler_path, args)

    def _start_process(self, program, args):
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.output_panel.append_output("[Runner] A process is already running.", is_error=True)
            return

        self.output_panel.clear_output()
        self.output_panel.append_output(f"[{self._current_task_info.get('name', 'Process')}] Starting...")
        self.output_panel.append_output(f"> {os.path.basename(program)} {' '.join(args)}\n")

        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        self.process.setWorkingDirectory(os.path.dirname(program))

        self.stop_action.setEnabled(True)
        self.process.start(program, args)

    def _handle_stdout(self):
        if self.process: self.output_panel.append_output(
            self.process.readAllStandardOutput().data().decode(errors='replace'))

    def _handle_stderr(self):
        if self.process: self.output_panel.append_output(
            self.process.readAllStandardError().data().decode(errors='replace'), is_error=True)

    def _handle_finished(self, exit_code, exit_status):
        task_name = self._current_task_info.get('name', 'Process')
        task_type = self._current_task_info.get('type')

        if task_type == 'compile':
            if exit_code == 0:
                self.output_panel.append_output(f"\n[{task_name}] Compilation successful.")
                runner_path = self._current_task_info.get('runner_path')
                self._current_task_info = {'name': f"{task_name.split(' ')[0]} Execution", 'type': 'run',
                                           'runner_path': runner_path}
                self._start_process(runner_path, [])
            else:
                self.output_panel.append_output(f"\n[{task_name}] Compilation failed.", is_error=True)
                self._on_run_finished(exit_code)
        else:  # Standard run or second step of compile-run
            self.output_panel.append_output(f"\n[{task_name}] Finished with exit code {exit_code}.")
            runner_path = self._current_task_info.get('runner_path')
            if runner_path and os.path.exists(runner_path) and self._current_task_info.get('type') != 'python_script':
                try:
                    os.remove(runner_path)
                except OSError as e:
                    self.output_panel.append_output(f"Could not remove temporary file: {e}", is_error=True)
            self._on_run_finished(exit_code)

    def _on_run_finished(self, exit_code):
        self.stop_action.setEnabled(False)
        self.process = None
        self._current_task_info = {}
        # Re-evaluate which run button should be active
        self._on_tab_changed(self.main_window.tab_widget.currentIndex())


def initialize(puffin_api: PuffinPluginAPI):
    return ScriptRunnerPlugin(puffin_api)
```
