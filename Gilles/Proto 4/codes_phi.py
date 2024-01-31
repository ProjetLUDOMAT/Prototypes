from time import sleep_ms

# Philips
codes = {
#     b'400\r\n':'0',
    b'401\r\n':'1',
    b'402\r\n':'2',
    b'403\r\n':'3',
    b'404\r\n':'4',
    b'405\r\n':'5',
    b'406\r\n':'6',
    b'407\r\n':'7',
    b'408\r\n':'8',
    b'409\r\n':'9',
    b'45A\r\n':'l',
    b'45B\r\n':'r',
    b'458\r\n':'u',
    b'459\r\n':'d',
    b'45C\r\n':'0',      # touche ok
    b'10483\r\n':'e',    # touche return
    b'40C\r\n':'o'       # touche on/off
    }

def decode_ir(u):
    if u.any():
        sleep_ms(500)
        cmd = u.read()
        for k in codes.keys():
            if k in cmd:
                return codes[k]