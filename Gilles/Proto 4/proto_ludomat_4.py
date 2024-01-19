from pwmStepper import *
from machine import Pin, UART
from time import sleep_ms, ticks_ms
#######  IR remote list
# from codes_sam import codes, decode_ir
# from codes_pan import codes, decode_ir
# from codes_phi import codes, decode_ir
from codes_chi import codes, decode_ir

m0 = pwmStep(id=0, stepSize=9.478673e-4, stepUnit='tr', max_speed=2)   # en tours
m1 = pwmStep(id=1, stepSize=9.478673e-4, stepUnit='tr', max_speed=2)

m0.setSpeed(0.5)    # en tr/s
m1.setSpeed(0.5)
m0.disable()
m1.disable()

u = UART(1, 9600)
u.init(tx=Pin(8), rx=Pin(9))

one_move = 1062
one_turn = 673

############

def forward():
    m0.doSteps(one_move)
    m1.doSteps(one_move)
    while m0.running or m1.running:
        sleep_ms(100)
    m0.disable()
    m1.disable()

def backward():
    m0.doSteps(-one_move)
    m1.doSteps(-one_move)
    while m0.running or m1.running:
        sleep_ms(100)
    m0.disable()
    m1.disable()

def turnleft():
    m0.doSteps(one_turn)
    m1.doSteps(-one_turn)
    while m0.running or m1.running:
        sleep_ms(100)
    m0.disable()
    m1.disable()

def turnright():
    m0.doSteps(-one_turn)
    m1.doSteps(one_turn)
    while m0.running or m1.running:
        sleep_ms(100)
    m0.disable()
    m1.disable()

def execute():
    for mvt in mvt_list:
        print(mvt)
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
#         led.toggle()
    elif cmd == '0':                  # ok
        execute()
    elif cmd == 'e':                  # enter
#         led.off()
        break
    elif cmd:
        mvt = cmd_dict[cmd]
        if mode_prog:
            mvt_list.append(mvt)
        else:
#             print(mvt)
            sleep_ms(1000)
            mvt()