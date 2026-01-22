from os import environ
import sys
import argparse
from xtermcolor.ColorMap import (
    TrueColorMap,
    XTermColorMap,
    VT100ColorMap,
    NoneColorizer,
    _rgb,
)
from xtermcolor._version import version

type RgbTriplet = list[int, int, int]
type AnsiColor = int
type RgbColor = int


def cPrintfString(color: AnsiColor | RgbColor, rgb: bool = False) -> str:
    if rgb:
        r, g, b = _rgb(color)
        return f"\\x1b\x5b38:2:{r}:{g}:{b}m"
    else:
        return f'"\\x1b\x5b38;5;{color}m%s\\x1b\x5b0m"'


def Cli():
    parser = argparse.ArgumentParser(
            description='xtermcolor: 256 terminal color library')

    parser.add_argument('action',
                        choices=['convert', 'list'],
                        help='Actions')

    parser.add_argument('--color',
                        help='Color to convert')

    parser.add_argument('--compat',
                        choices=['xterm', 'vt100'],
                        default='xterm',
                        help='Compatibility mode.  Defaults to xterm.')

    parser.add_argument("--version", action="version", version=f"%(prog)s {version}")

    cli = parser.parse_args()

    if cli.compat.lower() not in ['xterm', 'vt100']:
        sys.stderr.write('Error: --compat must be xterm or vt100\n')
        sys.exit(-1)

    colorMap = NoneColorizer()
    if environ.get("NO_COLOR", None) in [None, ""]:
        if TrueColorMap.check_support(sys.stdout.fileno()):
            colorMap = TrueColorMap()
        elif cli.compat.lower().startswith('xterm'):
            colorMap = XTermColorMap()
        elif cli.compat.lower() == 'vt100':
            colorMap = VT100ColorMap()

    match cli.action:
        case 'list':
            match colorMap:
                case TrueColorMap():
                    for ansicolor, hexcolor in colorMap.getColors().items():
                        print(colorMap.colorize(f"ansi={ansicolor}; rgb=#{hexcolor:06x}; printf={cPrintfString(hexcolor, rgb=True)}", rgb=hexcolor))
                case XTermColorMap():
                    for ansicolor, hexcolor in colorMap.getColors().items():
                        print(colorMap.colorize(f"ansi={ansicolor}; rgb=#{hexcolor:06x}; printf={cPrintfString(ansicolor)}", ansi=ansicolor))
                case VT100ColorMap():
                    for ansicolor, hexcolor in colorMap.getColors().items():
                        print(colorMap.colorize(f"ansi={ansicolor}; rgb=#{hexcolor:06x}; printf={cPrintfString(ansicolor)}", ansi=ansicolor))
                case NoneColorizer():
                    for ansicolor, hexcolor in colorMap.getColors().items():
                        print(colorMap.colorize(f"ansi={ansicolor}; rgb=#{hexcolor:06x}; printf={cPrintfString(ansicolor)}", ansi=ansicolor))

                # print(string.format(xterm=ansicolor, hexcolor=hexcolor, cprintf=cPrintfString(ansicolor)));
        case 'convert':
            if not cli.color:
                sys.stderr.write('Error: must specify --color\n')
                sys.exit(-1)
            if cli.color[0] == '#':
                cli.color = '0x' + cli.color[1:]
            cli.color = int(cli.color, 16)

            colorizedMsg = colorMap.colorize('The quick brown fox jumped over the lazy dog.', cli.color)
            (ansi, rgb) = colorMap.convert(cli.color)
            print("#{start:06x} is closest to #{closest:06x} which is ANSI code {ansi:d}\n".format( \
                    start=cli.color, closest=rgb, ansi=ansi))
            print("Example: " + colorizedMsg)
            print("printf() string: " + cPrintfString(ansi))
