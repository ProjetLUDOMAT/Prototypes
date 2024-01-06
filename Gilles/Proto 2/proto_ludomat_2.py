from dcMotor import dcMotor
from PioEncoder import encoder
from machine import Pin, UART
from time import sleep_ms, ticks_ms
from math import copysign
#######  IR remote list
# from codes_sam import codes, decode_ir
# from codes_pan import codes, decode_ir
# from codes_phi import codes, decode_ir
from codes_chi import codes, decode_ir

mg = dcMotor()
md = dcMotor(pin1=16, pin2=17, pinEn=18)

eng = encoder(ppr=21)
end = encoder(sm_id=1, pin1=2, pin2=3, ppr=21)

u = UART(1, 9600, rx=Pin(5), tx=Pin(4))

##### Asservissement position
dead_zone = 1
max_speed, min_speed = 100, 60

kp = 8.

def go_position(tgt_count1=0, tgt_count2=0):
    eng.stop = False
    end.stop = False
    last_pos1 = eng.get_count()
    last_pos2 = end.get_count()
    tim       = ticks_ms()
    while (not eng.stop) or (not end.stop):
        if (dt := ticks_ms() - tim) >= 50:
            tim = ticks_ms()

            if not eng.stop and ((abs(tgt_count1 - eng.get_count()) > dead_zone or abs(eng.speed) > min_speed)):
                err  = tgt_count1 - eng.count
                last_pos1 = eng.count
                speed = kp * err
                speed = max(-max_speed, min(speed, max_speed))
                if abs(speed) < min_speed:
                    speed = copysign(min_speed, speed)
                if eng.get_speed() == 0:
                    mg.set_speed(max_speed)
                mg.set_speed(speed)
            else:
                mg.stop()
                eng.stop = True

            if not end.stop and ((abs(tgt_count2 - end.get_count()) > dead_zone or abs(end.speed) > min_speed)):
                err  = tgt_count2 - end.count
                last_pos2 = end.count
                speed = kp * err
                speed = max(-max_speed, min(speed, max_speed))
                if abs(speed) < min_speed:
                    speed = copysign(min_speed, speed)
                if end.get_speed() == 0:
                    md.set_speed(max_speed)
                md.set_speed(speed)
            else:
                md.stop()
                end.stop = True
############

while True:
    cmd = decode_ir(u)
    if cmd: print(cmd)
    if cmd == 'u':
        mg.stop()
        md.stop()
        sleep_ms(300)
        eng.reset_count()
        end.reset_count()
        go_position(20, 20)
    elif cmd == 'd':
        mg.stop()
        md.stop()
        sleep_ms(300)
        eng.reset_count()
        end.reset_count()
        go_position(-20, -20)
    elif cmd == 'l':
        mg.stop()
        md.stop()
        sleep_ms(300)
        eng.reset_count()
        end.reset_count()
        go_position(-10, 10)
    elif cmd == 'r':
        mg.stop()
        md.stop()
        sleep_ms(300)
        eng.reset_count()
        end.reset_count()
        go_position(10, -10)
    elif  cmd == '0':
        mg.stop()
        md.stop()
    elif cmd == 'e':
        break