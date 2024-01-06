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

ml = dcMotor()                            # motor left
mr = dcMotor(pin1=16, pin2=17, pinEn=18)  # motor right

enl = encoder(ppr=1450)                           # encoder left
enr = encoder(sm_id=1, pin1=2, pin2=3, ppr=1450)  # encoder right

u = UART(1, 9600, rx=Pin(5), tx=Pin(4)) # communication avec ESP01 (diode IR)

##### Asservissement position
dead_zone = 3
max_speed, min_speed = 45, 35           # rapports cycliques max et min des moteurs

kp, kd = 1., 0.03   #  coefficient prop. et dérivée du correcteur PID

def go_position(tgt_count1=0, tgt_count2=0):   # PID vers la position (tgt_count_1, tgt_count2)
    enl.stop = False                           # tolerance = tgt_count +- dead_zone
    enr.stop = False
    last_pos1 = enl.get_count()
    last_pos2 = enr.get_count()
    tim       = ticks_ms()
#   boucle du PID
    while (not enl.stop) or (not enr.stop):
        if (dt := ticks_ms() - tim) >= 10:  # fréquence de boucle = 100 Hz
            tim = ticks_ms()

#           calcul commande moteur gauche
            if not enl.stop and ((abs(tgt_count1 - enl.get_count()) > dead_zone or abs(enl.speed) > min_speed)):
                err  = tgt_count1 - enl.count
                derr = (enl.count - last_pos1)/dt*1000
                last_pos1 = enl.count
                speed = kp * err - kd * derr
                speed = max(-max_speed, min(speed, max_speed))
                if abs(speed) < min_speed:
                    speed = copysign(min_speed, speed)
                if enl.get_speed() == 0:   # kick au démarrage
                    ml.set_speed(100)
                ml.set_speed(speed)
            else:
                ml.stop()
                enl.stop = True
#           calcul commande moteur droit
            if not enr.stop and ((abs(tgt_count2 - enr.get_count()) > dead_zone or abs(enr.speed) > min_speed)):
                err  = tgt_count2 - enr.count
                derr = (enr.count - last_pos2)/dt*1000
                last_pos2 = enr.count
                speed = kp * err - kd * derr
                speed = max(-max_speed, min(speed, max_speed))
                if abs(speed) < min_speed:
                    speed = copysign(min_speed, speed)
                if enr.get_speed() == 0:   # kick au démarrage
                    mr.set_speed(100)
                mr.set_speed(speed)
            else:
                mr.stop()
                enr.stop = True
############

while True:
    cmd = decode_ir(u)
    if cmd == 'u':
        ml.stop()
        mr.stop()
        sleep_ms(300)
        enl.reset_count()
        enr.reset_count()
        go_position(1063, 1063)
    elif cmd == 'd':
        ml.stop()
        mr.stop()
        sleep_ms(300)
        enl.reset_count()
        enr.reset_count()
        go_position(-1063, -1063)
    elif cmd == 'l':
        ml.stop()
        mr.stop()
        sleep_ms(300)
        enl.reset_count()
        enr.reset_count()
        go_position(-610, 610)
    elif cmd == 'r':
        ml.stop()
        mr.stop()
        sleep_ms(300)
        enl.reset_count()
        enr.reset_count()
        go_position(610, -610)
    elif  cmd == '0':
        ml.stop()
        mr.stop()
    elif cmd == 'e':
        break