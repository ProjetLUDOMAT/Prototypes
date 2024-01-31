from time import sleep_ms

# Telecomande chinoise
codes = {
    b'1FEE41B\r\n':'e',  # touche return
    b'1FEEC13\r\n':'l',
    b'1FE9C63\r\n':'r',
    b'1FE1CE3\r\n':'u',
    b'1FE02FD\r\n':'d',
    b'1FEC837\r\n':'0',  # touche ok
    b'1FEE11E\r\n':'+',
    b'1FE916E\r\n':'-',
    b'1FE12ED\r\n':'m',  # touche mouse
    b'1FECE31\r\n':'h',  # touche home
    b'1FE817E\r\n':'o'   # touche on/off
    }

def decode_ir(u):
    if u.any() >= 9:
        cmd = u.readline()
        if cmd in codes.keys():
            return codes[cmd]
