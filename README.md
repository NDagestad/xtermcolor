Fork
====

This is a fork of the original [xtermcolor](https://github.com/broadinstitute/xtermcolor).
The original project used a hard-coded list of terminal names to guess support for colors.

This version tries to be clever-er by using the XTGETCAP escape sequence to query the terminal 
for support before falling back the original behavior.

It also adds true 24bit color support when the terminal supports it, instead of falling back to the
closes index color to the RGB color requested.

Mostly, it should be a drop-in replacement of the original library.


XTermColor: Easy Terminal Colors
================================

XTermColor is a convenient python module for quickly colorizing text for output to the terminal
either via ANSI color code or RGB color value.  Support 256 colors!

![xtermcolor list](https://github.com/ndagestad/xtermcolor/raw/master/img/list.png)

Installation
------------

With [pip](http://www.pip-installer.org/en/latest/)

```bash
$ pip install .
```

Or, to just build a wheel:

```bash
$ python -m build --wheel
```

Command Line Usage
------------------

    $ xtermcolor --help
    usage: xtermcolor [-h] [--color COLOR] [--compat {xterm,vt100}] {convert,list}

    xtermcolor: 256 terminal color library

    positional arguments:
      {convert,list}        Actions

    optional arguments:
      -h, --help            show this help message and exit
      --color COLOR         Color to convert
      --compat {xterm,vt100}
                            Compatibility mode. Defaults to xterm.

To convert an RGB value to a printf() string or the closest ANSI color code, use `xtermcolor
convert` as follows:

![xtermcolor convert](https://github.com/ndagestad/xtermcolor/raw/master/img/convert.png)

Python Module Usage
-------------------

Simply import the `colorize` function from the `xtermcolor` module.  `colorize()` is always called
with a string as the first argument, but has a number of keyword arguments that can be specified:

* `rgb` - String of the RGB color value to color the text as.
* `ansi` - Integer value of the ANSI color code.
* `bg` - String of the RGB color value for the background color.
* `ansi_bg` - Integer value of ANSI color code for background color.
* `fd` - File descriptor that will be used to print the text.  Defaults to stdout.

arguments `rgb` and `ansi` are mutually exclusive, as are `bg` and `ansi_bg`.

![xtermcolor module](https://github.com/ndagestad/xtermcolor/raw/master/img/module.png)
