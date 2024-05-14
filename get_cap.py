import binascii
import sys
import os

import termios
import tty


DCS='\x1bP+q{}\x1b\\'

def req(capability):

    print(capability)
    tty_fd = os.open('/dev/tty', os.O_RDWR | os.O_NOCTTY)
    fd = open(tty_fd, 'r+b', 0)

    # Switch to raw mode
    os.set_blocking(tty_fd,False)
    tty_attrs = termios.tcgetattr(tty_fd)
    tty.setraw(tty_fd)

    fd.write(DCS.format(binascii.hexlify(capability)).encode())
    response = fd.read(1024)

    # Restore terminal to cooked mode
    termios.tcsetattr(tty_fd, termios.TCSAFLUSH, tty_attrs)

    print(response)
    fd.close()

req(b"colors")
