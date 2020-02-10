'''Defines ANSI escape codes for convenience.'''

# See also
# https://en.wikipedia.org/wiki/ANSI_escape_code#Escape_sequences

END = '\033[0m'
BOLD = '\033[1m'
FAINT = '\033[2m'
ITALIC = '\033[2m'
UNDERLINE = '\033[4m'
NEGATIVE = '\033[7m'
CPL = '\033[F'
EIL = '\033[2K'
TTYJUMP = CPL + EIL


ALL_SYMBOLS = [END, BOLD, FAINT, ITALIC, UNDERLINE, NEGATIVE, TTYJUMP]
