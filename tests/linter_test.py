# PuffinPyEditor/tests/linter_test.py
"""
PuffinPyEditor - Linter Test Script (Comprehensive)

This single file contains numerous, non-fatal errors and style violations
to test the 'Problems' panel. When opened, all issues listed below
should appear simultaneously.
"""

# F401: 'os' imported but unused
# F401: 'time' imported but unused
import os, time

# E501: line too long (88 > 79 characters)
a_very_long_variable_name_designed_to_intentionally_exceed_the_pep8_line_length_limit = "too long"


# F841: local variable 'unused_variable' is assigned to but never used
def function_with_unused_variable():
    unused_variable = 100
    print("This function has an unused variable.")


# E302: expected 2 blank lines, found 1
class BadStyle:
    # E225: missing whitespace around operator
    def __init__(self, val=1):
        self.value = val

    # F821: undefined name 'some_undefined_variable'
    # This is a runtime error, but not a fatal syntax error, so it should be detected alongside style issues.
    def use_undefined_name(self):
        print(some_undefined_variable)


# E701: multiple statements on one line (colon)
print("first statement");
print("second statement")

# W293: blank line contains whitespace (add a space or tab to the blank line below)


# E111: indentation is not a multiple of four (this line has 1 space)
print("This line has incorrect indentation.")

# W292: no newline at end of file
# This error will appear if you save the file without a blank line at the very end.

