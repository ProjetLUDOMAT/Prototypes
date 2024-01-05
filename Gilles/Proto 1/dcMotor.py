###########################################################################################
#
#  Driver Raspberry Pico pour L293D (voir driver_L293D.pdf)
#
###########################################################################################

from machine import Pin, PWM
from math import copysign

class dcMotor():

    def __init__(self, pin1=14, pin2=15, pinEn=13, freq=1000):
        ''' pin1, pin2: commande du pont en H
            pinEn: pin enable du pont en H
            freq: frequence de hachage
        '''
        self.pin1 = Pin(pin1, Pin.OUT)
        self.pin2 = Pin(pin2, Pin.OUT)
        self.pwm = PWM(Pin(pinEn))
        self.freq = freq
        self.dir = 1
        self.duty = 0
        self.duty_offset = 0  # minimum value
        self.speed = 0
        self.pwm.freq(freq)
        self.set_dir(self.dir)
        self.stop()

    def set_dir(self, dir):
        self.pin1.value(dir==1)
        self.pin2.value(dir==-1)
        self.speed = dir*abs(self.speed)

    def set_duty(self, duty):
        ''' duty 0 -> 100%'''
        self.set_dir(1 if duty >=0 else -1)
        self.pwm.duty_u16(int(abs(duty)*655.35))
        self.duty = duty

    def set_speed(self, speed):
        ''' speed 0 -> 100% '''
        if speed == 0:
            self.speed = 0
            self.set_duty(0)
        else:
            duty = self.duty_offset + (100 - self.duty_offset)*abs(speed)/100
            duty = copysign(duty, speed)
            self.set_duty(duty)

    def stop(self):
        self.set_speed(0)
