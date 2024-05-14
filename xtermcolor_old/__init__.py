from os import isatty, environ, write

from xtermcolor.ColorMap import XTermColorMap, VT100ColorMap, NoneColorizer

outputs = {}

def colorize(string, rgb=None, ansi=None, bg=None, ansi_bg=None, fd=1):
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
        outputs[fd] = NoneColorizer()
        #Checks if it is on a terminal, and if the terminal is recognized
        if isatty(fd) and 'TERM' in environ:
            match environ['TERM']:
                case _ if environ['TERM'].startswith('xterm'):
                    print("In the first match")
                    outputs[fd] = XTermColorMap()
                case 'vt100':
                    outputs[fd] = VT100ColorMap()
                case 'foot':
                    outputs[fd] = XTermColorMap()

    return outputs[fd].colorize(string, rgb, ansi, bg, ansi_bg)

