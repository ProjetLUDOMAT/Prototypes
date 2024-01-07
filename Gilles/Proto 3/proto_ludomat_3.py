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

u = UART(0, 9600)

one_move = 1027
one_turn = 738

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

############

while True:
    cmd = decode_ir(u)
    if cmd == 'u':
        forward()
    elif cmd == 'd':
        backward()
    elif cmd == 'l':
        turnleft()
    elif cmd == 'r':
        turnright()
    elif  cmd == '0':
        pass
    elif cmd == 'e':
        break