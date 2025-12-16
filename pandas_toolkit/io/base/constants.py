"""
Common constants for file readers.
"""

# Common encoding options to try when reading files
COMMON_ENCODINGS = [
    "utf-8",         # Most common encoding, compatible with ASCII
    "utf-8-sig",     # UTF-8 with BOM (Byte Order Mark)
    "cp1252",        # Windows-1252, Western European
    "latin1",        # ISO-8859-1 alias
    "iso-8859-1",    # ISO Latin-1
    "utf-16",        # Unicode 16-bit with BOM
    "utf-16-le",     # UTF-16 little-endian
    "utf-16-be",     # UTF-16 big-endian
    "utf-32",        # Unicode 32-bit
    "utf-32-le",     # UTF-32 little-endian
    "utf-32-be",     # UTF-32 big-endian
    "cp1250",        # Central European Windows
    "cp1251",        # Cyrillic Windows (Russian, Bulgarian, etc.)
    "cp1253",        # Greek Windows
    "cp1254",        # Turkish Windows
    "cp932",         # Japanese Shift JIS variant
    "shift_jis",     # Standard Japanese Shift JIS
    "euc-jp",        # Japanese EUC
    "euc-kr",        # Korean EUC
    "big5",          # Traditional Chinese (Taiwan, Hong Kong)
    "gb2312",        # Simplified Chinese
    "mac_roman",     # Old Mac OS Western
    "ascii",         # Basic 7-bit encoding
]

# Common delimiters used in delimited text files
COMMON_DELIMITERS = [
    ",",             # Comma (most common)
    ";",             # Semicolon (European CSVs)
    "\t",            # Tab (TSV files)
    "|",             # Pipe
    ":",             # Colon
    "~",             # Tilde
    "^",             # Caret
    "#",             # Hash
    " ",             # Space
    "_",             # Underscore
    "-",             # Hyphen
    "/",             # Forward slash
    "\\",            # Backslash
    "*",             # Asterisk
    "=",             # Equals
    "'",             # Single quote
    "\"",            # Double quote
]

# Excel engines to try based on file format
EXCEL_ENGINES = {
    ".xlsx": ["openpyxl", "xlrd"],      # Modern Excel files
    ".xls": ["xlrd", "openpyxl"],       # Legacy Excel files
    "default": ["openpyxl", "xlrd"]     # Default fallback
}

# Engine availability per format (optimization: avoid trying unavailable engines)
EXCEL_ENGINES_BY_FORMAT = {
    ".xlsx": "openpyxl",    # Primary engine for modern Excel
    ".xls": "xlrd"          # Primary engine for legacy Excel
}