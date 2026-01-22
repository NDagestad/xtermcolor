from os import isatty, environ
from xtermcolor.ColorMap import (
    TrueColorMap,
    XTermColorMap,
    VT100ColorMap,
    NoneColorizer,
)

outputs = {}


type RgbTriplet = list[int, int, int]
type AnsiColor = int
type RgbColor = int


def colorize(
        string: str,
        rgb: RgbColor = None,
        ansi: AnsiColor = None,
        bg: RgbColor = None,
        ansi_bg: AnsiColor = None,
        fd: int = 1,
        ) -> str:
    '''Returns the colored string to print on the terminal.

    This function detects the terminal type and if it is supported and the
    output is not going to a pipe or a file, then it will return the colored
    string, otherwise it will return the string without modifications.

    string = the string to print. Only accepts strings, unicode strings must
             be encoded in advance.
    rgb    = Rgb color for the text; for example 0xFF0000 is red.
    ansi   = Ansi for the text
    bg     = Rgb color for the background
    ansi_bg= Ansi color for the background
    fd     = The file descriptor that will be used by print, by default is the
             stdout
    '''

    if outputs.get(fd) is None:
        # Let's be good stewards of the ecosystem
        # https://no-color.org/
        outputs[fd] = NoneColorizer()
        if environ.get("NO_COLOR", None) in [None, ""] and isatty(fd):
            # Try to autodetect support
            if TrueColorMap.check_support(fd):
                outputs[fd] = TrueColorMap()

            # Legacy checks based on TERM
            match environ['TERM']:
                case _ if environ['TERM'].startswith('xterm'):
                    outputs[fd] = XTermColorMap()
                case 'vt100':
                    outputs[fd] = VT100ColorMap()

    return outputs[fd].colorize(string, rgb, ansi, bg, ansi_bg)


__ALL__ = [colorize]
