from time import sleep_ms

# Panasonic
codes = {
    b'4004053898A5\r\n':'0',
    b'400405380835\r\n':'1',
    b'4004053888B5\r\n':'2',
    b'400405384875\r\n':'3',
    b'40040538C8F5\r\n':'4',
    b'400405382815\r\n':'5',
    b'40040538A895\r\n':'6',
    b'400405386855\r\n':'7',
    b'40040538E8D5\r\n':'8',
    b'400405381825\r\n':'9',
    b'40040544ECAD\r\n':'l',
    b'400405446C2D\r\n':'r',
    b'400405442C6D\r\n':'u',
    b'40040544ACED\r\n':'d',
    b'400405446322\r\n':'e',
    b'400405000401\r\n':'+',
    b'400405008481\r\n':'-'
    }

def decode_ir(u):
    if u.any():
        sleep_ms(300)
        cmd = u.read()
        for k in codes.keys():
            if k in cmd:
                return codes[k]