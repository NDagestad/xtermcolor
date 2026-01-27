from xtermcolor.term_esc_sequence import execute as term_esc_exec
import os


class TerminalColorMapException(Exception):
    pass


type RgbTriplet = list[int, int, int]
type AnsiColor = int
type RgbColor = int


def _rgb(color: RgbColor) -> RgbTriplet:
    return ((color >> 16) & 0xff, (color >> 8) & 0xff, color & 0xff)


def _diff(color1: AnsiColor, color2: AnsiColor) -> AnsiColor:
    '''Compute a distance between 2 colors'''
    (r1, g1, b1) = _rgb(color1)
    (r2, g2, b2) = _rgb(color2)
    return abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)


class TerminalColorMap:
    def __init__(self):
        self.colors = dict()
        self._compute()

    def _compute(self):
        '''Nothing to compute for the parent class'''
        pass

    def getColors(self, order='rgb') -> AnsiColor:
        return self.colors

    def convert(self, hexcolor: RgbColor) -> tuple[AnsiColor, RgbColor]:
        '''Convert a RgbColor to an AnsiColor and RgbColor tuple'''
        diffs = {}
        for xterm, rgb in self.colors.items():
            diffs[_diff(rgb, hexcolor)] = xterm
        minDiffAnsi = diffs[min(diffs.keys())]
        return (minDiffAnsi, self.colors[minDiffAnsi])

    def colorize(
            self, string: str,
            rgb: RgbColor = None,
            ansi: AnsiColor = None,
            bg: RgbColor = None,
            ansi_bg: AnsiColor = None
            ) -> str:
        '''Returns the colored string'''
        if not isinstance(string, str):
            string = str(string)
        if rgb is None and ansi is None:
            raise TerminalColorMapException(
                'colorize: must specify one named parameter: rgb or ansi')
        if rgb is not None and ansi is not None:
            raise TerminalColorMapException(
                'colorize: must specify only one named parameter: rgb or ansi')
        if bg is not None and ansi_bg is not None:
            raise TerminalColorMapException(
                'colorize: must specify only one named parameter: bg or ansi_bg')

        if rgb is not None:
            (closestAnsi, _) = self.convert(rgb)
        elif ansi is not None:
            (closestAnsi, _) = (ansi, self.colors[ansi])

        if bg is None and ansi_bg is None:
            return f"\x1b\x5b38;5;{closestAnsi}m{string}\x1b\x5b0m"

        if bg is not None:
            (closestBgAnsi, _) = self.convert(bg)
        elif ansi_bg is not None:
            (closestBgAnsi, _) = (ansi_bg, self.colors[ansi_bg])

        return (
            f"\x1b\x5b38;5;{closestAnsi:d}m\x1b\x5b48;5;"
            f"{closestBgAnsi:d}m{string:s}\x1b\x5b0m"
        )


class NoneColorizer(TerminalColorMap):
    def colorize(
            self, string: str,
            # Ignore all other arguments
            *aregs,
            **kwargs,
            ) -> str:
        '''Just print the string without any changes'''
        return string


class VT100ColorMap(TerminalColorMap):
    '''3 or 4-bit color terminals'''
    primary = [
        0x000000, 0x800000, 0x008000, 0x808000,
        0x000080, 0x800080, 0x008080, 0xc0c0c0
    ]

    bright = [
        0x808080, 0xff0000, 0x00ff00, 0xffff00,
        0x0000ff, 0xff00ff, 0x00ffff, 0xffffff
    ]

    def _compute(self):
        '''Fill out the color attribute'''
        for index, color in enumerate(self.primary + self.bright):
            self.colors[index] = color


class XTermColorMap(VT100ColorMap):
    '''8-bit coloir terminal'''

    grayscale_start = 0x08
    grayscale_end = 0xf8
    grayscale_step = 10
    intensities = [0x00, 0x5F, 0x87, 0xAF, 0xD7, 0xFF]

    def _compute(self):
        '''Fill out the color attribute'''
        for index, color in enumerate(self.primary + self.bright):
            self.colors[index] = color

        c = 16
        for i in self.intensities:
            color = i << 16
            for j in self.intensities:
                color &= ~(0xff << 8)
                color |= j << 8
                for k in self.intensities:
                    color &= ~0xff
                    color |= k
                    self.colors[c] = color
                    c += 1

        c = 232
        for hex in list(range(self.grayscale_start,
                              self.grayscale_end,
                              self.grayscale_step)):
            color = (hex << 16) | (hex << 8) | hex
            self.colors[c] = color
            c += 1


class TrueColorMap(XTermColorMap):
    '''25-bit color terminal'''

    # \E[>c │ DA2 │ VT220 │ Send secondary device attributes. Foot responds with "I'm a VT220 and here's my version number".  # ]
    @classmethod
    def check_support(cls, fd: int) -> bool:
        # Check support in termcap and terminfo introduced in SVr3.2 (1987)
        color_support = term_esc_exec("colors")
        if len(color_support) == 0:
            return False
        if color_support[0] is not None and int(color_support) >= 256:
            return True

        # Try to first get the TERM through XTGETTCAP
        term = term_esc_exec("TN")[0]
        if term is None:
            term = os.environ.ger("TERM", None)

        # check terminfo for support
        # check if TERM is in a hard-coded list of known supported terminals
        # Last ditch effort, check $COLORTERM variable
        return False

    def colorize(self, string, rgb=None, ansi=None, bg=None, ansi_bg=None):
        '''Returns the colored string'''
        if not isinstance(string, str):
            string = str(string)
        if rgb is None and ansi is None:
            raise TerminalColorMapException(
                'colorize: must specify one named parameter: rgb or ansi')
        if rgb is not None and ansi is not None:
            raise TerminalColorMapException(
                'colorize: must specify only one named parameter: rgb or ansi')
        if bg is not None and ansi_bg is not None:
            raise TerminalColorMapException(
                'colorize: must specify only one named parameter: bg or ansi_bg')

        fg_ansi_code = ""
        bg_ansi_code = ""
        ansi_code_end = "\x1b\x5b0m"

        if rgb is not None:
            (_, closestRgb) = self.convert(rgb)
            fg_r, fg_g, fg_b = _rgb(closestRgb)
            # Apparently the IS should have a first argument that is the colorspace
            # But since I don't know what that is, I will omit it for now given that
            # this is often the case and widely supported
            # XXX Maybe I should use the ; separated form instead?
            fg_ansi_code = f"\x1b\x5b38:2:{fg_r}:{fg_g}:{fg_b}m"
        elif ansi is not None:
            fg_ansi_code = f"\x1b\x5b38;5;{ansi}m"

        if bg is not None:
            (_, closestRgb) = self.convert(bg)
            bg_r, bg_g, bg_b = _rgb(closestRgb)
            bg_ansi_code = f"\x1b\x5b48:2:{bg_r}:{bg_g}:{bg_b}m"
        elif ansi_bg is not None:
            bg_ansi_code = f"\x1b\x5b38;5;{ansi_bg}m"

        return f"{fg_ansi_code}{bg_ansi_code}{string}{ansi_code_end}"
