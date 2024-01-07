# Samsung
codes = {
    b'E0E08877\r\n':'0',
    b'E0E020DF\r\n':'1',
    b'E0E0A05F\r\n':'2',
    b'E0E0609F\r\n':'3',
    b'E0E010EF\r\n':'4',
    b'E0E0906F\r\n':'5',
    b'E0E050AF\r\n':'6',
    b'E0E030CF\r\n':'7',
    b'E0E0B04F\r\n':'8',
    b'E0E0708F\r\n':'9',
    b'E0E0A659\r\n':'l',
    b'E0E046B9\r\n':'r',
    b'E0E006F9\r\n':'u',
    b'E0E08679\r\n':'d',
    b'E0E016E9\r\n':'e',
    b'E0E0E01F\r\n':'+',
    b'E0E0D02F\r\n':'-'
    }

def decode_ir(u):
    if u.any() >= 10:
        cmd = u.readline()
        if cmd in codes.keys():
            return codes[cmd]