from pwmStepper import *
from machine import Pin, UART
from time import sleep_ms, ticks_ms
from ws2812 import WS2812
from ws2812_colors import *
#######  IR remote list
import codes_chi
import codes_pan
import codes_phi

# init neopixel
led = WS2812(16,1)
led.pixels_fill(RED)
led.pixels_show()

# init leds direction
ledd = Pin(1, Pin.OUT)
ledg = Pin(2, Pin.OUT)
ledd.off()
ledg.off()

# init steppers
m0 = pwmStep(id=0, stepSize=9.478673e-4, stepUnit='tr', max_speed=2)   # stepSize en tr/pas
m1 = pwmStep(id=1, stepSize=9.478673e-4, stepUnit='tr', max_speed=2)   # max_speed en tr/s

m0.setSpeed(0.5)    # en tr/s
m1.setSpeed(0.5)
m0.disable()
m1.disable()

one_move = 1062
one_turn = 673

# init IR
u = UART(1, 9600)
u.init(tx=Pin(8), rx=Pin(9))

def find_remote():
    u.flush()
    while True:
        if u.any():
            sleep_ms(300)
            cmd = u.read()
            for k in codes_phi.codes.keys():
                if k in cmd:
                    print('télécommande Philips')
                    return 'Philips'
            for k in codes_pan.codes.keys():
                if k in cmd:
                    print('télécommande Panasonic')
                    return 'Panasonic'
            for k in codes_chi.codes.keys():
                if k in cmd:
                    print('télécommande chinoise')
                    return 'chinoise'

telec = find_remote()

if telec == 'Philips':
    from codes_phi import codes, decode_ir
elif telec == 'Panasonic':
    from codes_pan import codes, decode_ir
elif telec == 'chinoise':
    from codes_chi import codes, decode_ir

led.pixels_fill(GREEN)
led.pixels_show()

############

def forward():
    ledg.on()
    ledd.on()
    m0.doSteps(one_move)
    m1.doSteps(one_move)
    while m0.running or m1.running:
        sleep_ms(100)
    m0.disable()
    m1.disable()
    ledg.off()
    ledd.off()

def backward():
    m0.doSteps(-one_move)
    m1.doSteps(-one_move)
    while m0.running or m1.running:
        sleep_ms(100)
    m0.disable()
    m1.disable()

def turnleft():
    ledg.on()
    m0.doSteps(one_turn)
    m1.doSteps(-one_turn)
    while m0.running or m1.running:
        sleep_ms(100)
    m0.disable()
    m1.disable()
    ledg.off()

def turnright():
    ledd.on()
    m0.doSteps(-one_turn)
    m1.doSteps(one_turn)
    while m0.running or m1.running:
        sleep_ms(100)
    m0.disable()
    m1.disable()
    ledd.off()

def execute():
    for mvt in mvt_list:
        sleep_ms(1000)
        mvt()

cmd_dict  = {'u':forward, 'd':backward, 'l':turnleft, 'r':turnright}
mvt_list  = []
mode_prog = False

############

while True:
    cmd = decode_ir(u)
    if cmd == 'o':                    # on/off
        mvt_list = []
        mode_prog = not mode_prog
        if mode_prog:
            led.pixels_fill(BLUE)
            led.pixels_show()
        else:
            led.pixels_fill(GREEN)
            led.pixels_show()
    elif cmd == '0':                  # ok
        execute()
    elif cmd == 'e':                  # enter
        led.pixels_fill(BLACK)
        led.pixels_show()
        break
    elif cmd:
        mvt = cmd_dict[cmd]
        if mode_prog:
            mvt_list.append(mvt)
        else:
            sleep_ms(1000)
            mvt()