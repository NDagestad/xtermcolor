import codecs
import os
import select
import sys
import termios
import tty


def do_term_request(capability: (str | bytes | list), timeout: int = 0.1) -> list[str]:
    DCS = '\x1bP+q{}\x1b\\'

    # Handle str, bytes and lists of them
    if type(capability) in [str, bytes]:
        capability = [capability]

    # Convert any argument into a list semicolon separated hex-string
    if type(capability) in [list, tuple]:
        capability = ";".join([
            x.hex() if type(x) is bytes else x.encode().hex() for x in capability
        ])

    data = b""
    d = b""

    stdin_fd = sys.stdin.fileno()
    old_attr = termios.tcgetattr(stdin_fd)
    tty_fd = os.open('/dev/tty', os.O_RDWR | os.O_NOCTTY)
    fd = open(tty_fd, 'wb', 0)
    try:
        os.set_blocking(tty_fd, False)
        cmd = DCS.format(capability).encode()
        # Switch to raw mode
        tty.setraw(stdin_fd)
        # Write the code
        fd.write(cmd)
        # Read the response
        while True:
            r, _, _ = select.select([stdin_fd], [], [], timeout)
            if r:
                d = os.read(stdin_fd, 1024)
                data+=d
            else:
                break
    except Exception as e:
        raise e
    finally:
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_attr)
        fd.close()

    # split the data into individual responses
    parts = data.split(b"\x1b\\")
    # The last part should be empty because the string should end with b"\x1b\\"
    if parts[-1] != b"":
        return None

    return [x+b"\x1b\\" for x in parts[:-1]]


def parse_term_response(resp: bytes) -> (tuple[str, str] | None):
    # Everything should start with b"\x1bP1+r" and end with b"\x1b\\"
    if resp[0:5] != b"\x1bP1+r" or resp[-2:] != b"\x1b\\":
        # Don't know how to handle this
        return None, None
    resp = resp.removeprefix(b"\x1bP1+r").removesuffix(b"\x1b\\")

    # A response if of the form <hexName>=<hexValue>
    if b"=" in resp:
        name, val = resp.split(b"=")
        name = codecs.decode(name, 'hex')
        val = codecs.decode(val, 'hex')
    else:
        # This means the code is not supported; the name was returned without value
        return codecs.decode(resp, 'hex'), None
    return name, val


# Return a byte string or multiple bytes strings
def execute(*commands: (bytes | str | list), **kwargs) -> bytes:
    # Add logic to handle commands that takes arguments
    resp = do_term_request(commands)
    if resp is None:
        return []
    vals = []
    for r in resp:
        _, val = parse_term_response(r)
        vals.append(val)
    return vals


if __name__ == "__main__":
    resp = do_term_request(b"TN")[0]
    if resp is not None:
        print(parse_term_response(resp))
    else:
        print("Failed to execute 'TN'")

    resp = do_term_request(b"colors")[0]
    if resp is not None:
        print(parse_term_response(resp))
    else:
        print("Failed to execute 'colors'")

    responses = execute(b"colors", "TN")
    print(responses)
    responses = execute("TN", b"colors")
    print(responses)
