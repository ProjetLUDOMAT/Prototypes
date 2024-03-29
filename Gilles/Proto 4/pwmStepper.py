#########################################################################################
#
#   Driver for bipolar stepper without acceleration/deceleration - Steps triggered by PWM
#
#########################################################################################
#
from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from time import sleep_us
#
dirPins      = [7, 27]                # GPIO direction pin
stepPins     = [6, 26]                # GPIO step pin (pwm)
enablePins   = [0, 14]                # GPIO enable pin (0=enable, 1=disable)
stepResPins  = [[9, 8], [12, 13]]     # GPIOs step resolution pins [m0,m1]
pwm_sm       = [0, 2]                 # pwm state_machine id
cnt_sm       = [1, 3]                 # step counter state_machine id
driverList   = ['DRV8834', 'MP6500']  # list of implemented drivers
#
stepResList = {'DRV8834':{1:('L','L'), 2:('H','L'), 4:('F','L'),
                          8:('L','H'), 16:('H','H'), 32:('F','H')},
               'MP6500':{1:('L','L'), 2:('H','L'), 4:('L','H'),
                         8:('H','H')}}
#
STEP_MAX_TIME   = 20000                # max value of step duration in us
STEP_MAX_NB     = 0xffffffff           # max step nb
PWM_PULSE_WIDTH = 30                   # pulse width = 3 us

#
#   PIO state machine programs
#
@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_prog(sideset_init=PIO.OUT_LOW):
    wait(0, irq, rel(5))  .side(0)
    mov(x, isr)
    pull(noblock)
    mov(x, osr)
    mov(isr, x)
    label("pwmloop")
    jmp(x_not_y, "skip")
    nop() .side(1)
    irq(noblock, rel(5))
    label("skip")
    jmp(x_dec, "pwmloop")

@asm_pio()
def cnt_prog():
    irq(noblock, rel(4))
    pull(block)
    mov(x, osr)
    label("countloop")
    wait(1, irq, rel(4))
    jmp(x_dec, "countloop")
    irq(rel(0))
#
class pwmStep():

    def __init__(self, id=0, dev='DRV8834', stepRes=1, stepSize=0.147, stepUnit='mm',
                 max_speed=147, min_speed=0, invert=False):
        #
        if id not in (0,1):
            print('bpStepper.__init__ - Error : id ', id, ' invalid (must be 0, or 1')
            return
        #
        if dev not in driverList:
            print('bpStepper.__init__ - Error: driver ', dev, ' inconnu')
            return
        self.dev = dev
        #
        self.id = id
        # max step resolution
        max_step_res = max(stepResList[self.dev].keys())
        # Pin initialization
        self.dirPin    = Pin(dirPins[id] ,       Pin.OUT)
        self.stepPin   = Pin(stepPins[id],       Pin.OUT)
        self.enablePin = Pin(enablePins[id],     Pin.OUT)
        self.m0Pin     = Pin(stepResPins[id][0], Pin.OUT)
        self.m1Pin     = Pin(stepResPins[id][1], Pin.OUT)
        self.enablePin.value(1)                               # driver output disabled
        # motor attributes initialisation
        self.stepSize      = stepSize                         # full step size
        self.stepUnit      = stepUnit                         #
        self.resCountList  = {1:0, 2:0, 4:0, 8:0, 16:0, 32:0} # step counter by resolution
        self.stepRes       = stepRes                          # index of current resolution in stepList
        self.min_speed     = max(min_speed,                   # minimum speed
                                 1000000*stepSize/STEP_MAX_TIME/max_step_res)
        self.max_speed     = max_speed                        # maximum speed
        self.speed         = max_speed
        self.min_step_time = round(1000000*stepSize/max_speed/stepRes)  # minimum step time in us
        self.step_time     = self.min_step_time
        self.invert        = invert
        self.dir           = 1                                # direction
        # Print setup
        print('*********** Driver ', self.dev, 'initialization ***********')
        print('      dir pin                   : GPIO' + str(dirPins[id]))
        print('      step pin                  : GPIO' + str(stepPins[id]))
        print('      enable pin                : GPIO' + str(enablePins[id]))
        print('      step resolution pins      :[GPIO' + str(stepResPins[id][0]) + ', GPIO' + str(stepResPins[id][1]) + ']')
        print('      full step size            :', self.stepSize, self.stepUnit)
        print('      min/max speed             :', self.min_speed, '/', self.max_speed, self.stepUnit, '/s')
        print('      minimum (full)step time   :', self.min_step_time, 'us')
        # init pwm state machine
        self.pwm_sm = StateMachine(pwm_sm[id], pwm_prog, freq=20_000_000, sideset_base=self.stepPin)
        self.pwm_sm.put(PWM_PULSE_WIDTH)
        self.pwm_sm.exec("pull()")
        self.pwm_sm.exec("mov(y, osr)")
        # init step counter state machine
        self.cnt_sm = StateMachine(cnt_sm[id], cnt_prog, freq=20_000_000)
        self.cnt_sm.irq(self.stepsEnd)
        #
        self.running = False
        # Set initial resolution
        self.setRes(stepRes)
        # set initial speed
        self.setSpeed(self.speed)
        # start pwm and cnt state machines
        self.cnt_sm.active(True)
        self.pwm_sm.active(True)

    def setRes(self, stepRes, silent=True):
        ''' Set step resolution: 1=full step, 2=1/2 step, 4=1/4 step ... '''
        def setPinState(pin, state):
            if state == 'F':
                pin.init(Pin.OPEN_DRAIN)
                pin.value(1)
            else:
                pin.init(Pin.OUT)
                pin.value(state == 'H')
        # check if resolution is supported
        if stepRes not in stepResList[self.dev].keys():
            print('Error: step size 1/', stepRes, ' invalid for device ', self.dev)
            return
        # set resolution pins
        setPinState(self.m0Pin, stepResList[self.dev][stepRes][0])
        setPinState(self.m1Pin, stepResList[self.dev][stepRes][1])
        self.stepRes = stepRes
        # compute new step duration
        self.step_time = round(1000000*self.stepSize/abs(self.speed)/self.stepRes)  # in us
        # check step duration
        if self.step_time > STEP_MAX_TIME:
            self.step_time = STEP_MAX_TIME
            self.speed     = self.dir*1000000*self.stepSize/self.step_time/self.stepRes
            print('*** Warning *** maximum step time reached, speed reduced to ', self.speed, self.stepUnit, '/s')
        # send new step duration to pwm state_machine
        #self.pwm_sm.put(self.step_time*10)
        self.setSpeed(self.speed)
        if not silent:
            print('Step resolution set to : 1/', self.stepRes, '  step period=', self.step_time, 'us')

    def getRes(self):
        return self.stepRes

    def enable(self):
        self.enablePin.value(0)

    def disable(self):
        self.enablePin.value(1)
        self.running = False

    def setDir(self, dir):
        ''' Forward if dir >= 0 => self.dir=1
            Backward if dir < 0 => self.dir=-1 '''
        self.dirPin.value((dir>=0)^self.invert)
        self.dir = 1 if dir > 0 else -1

    def getDir(self):
        return 1 if self.dirPin.value() else -1

    def getPosition(self):
        ''' compute position from resolution step count list '''
        pos = 0
        for k in self.resCountList.keys():
            pos += self.resCountList[k]*self.stepSize/k
        # if motor is running, read step count from counter state machine FIFO
        if self.running:
            self.cnt_sm.exec("mov(isr, x)")
            self.cnt_sm.exec("push()")
            pos += self.dir*(self.nsteps-self.cnt_sm.get())*self.stepSize/self.stepRes
        return pos

    def resetPosition(self):
        ''' reset position '''
        self.resCountList = {1:0, 2:0, 4:0, 8:0, 16:0, 32:0}

    def doSteps(self, nsteps):
        ''' move abs(nsteps) forward if nsteps > 0, backward otherwise '''
        if nsteps == 0:
            return
        elif abs(nsteps) > STEP_MAX_NB:
            print('nb of steps must be <=', STEP_MAX_NB)
            return
        self.nsteps = abs(nsteps)
        # set direction pin
        self.setDir(nsteps//self.nsteps)
        self.enable()
        self.running = True
        # send nsteps to step counter state_machine
        self.cnt_sm.put(self.nsteps)

    def stepsEnd(self, sm):
        ''' iqr handler - called when last step has been executed '''
        # check irq source
        if sm != self.cnt_sm:
            return
        # turn off driver
        self.disable()
        self.running = False
        # update position
        self.resCountList[self.stepRes] += self.dir*self.nsteps

    def stop(self):
        ''' stop motor (abort run) '''
        # stop cnt state-machine (stop pwm signal)
        self.cnt_sm.active(False)
        # read step (de)counter
        self.cnt_sm.exec("mov(isr, x)")
        self.cnt_sm.exec("push()")
        steps_left = self.cnt_sm.get()
        # update position
        self.resCountList[self.stepRes] += self.dir*(self.nsteps - steps_left)
        self.nsteps = 0
        # clear step counter
        self.cnt_sm.put(0)
        self.cnt_sm.exec("pull(noblock)")
        self.cnt_sm.exec("mov(x, osr)")
        # restart cnt state-machine
        self.cnt_sm.active(True)
        # turn off driver
        self.disable()
        self.running = False
        # update position


    def setSpeed(self, speed, silent=True):
        ''' set motor speed '''
        if abs(speed) < self.min_speed:
            self.pwm_sm.active(False)
            self.speed = 0
            return
        if self.speed == 0:
            self.pwm_sm.active(True)
        if abs(speed) > self.max_speed:
            print(' speed value too high, must be <=', self.max_speed, self.stepUnit,'/s')
            return
        self.setDir(speed)
        self.speed = speed
        # compute step duration
#         self.step_time = round(1000000*self.stepSize/self.speed/self.stepRes)   # in us
        self.step_time = round(1000000*self.stepSize/abs(speed)/self.stepRes)   # in us
        if self.step_time > STEP_MAX_TIME:
            self.step_time = STEP_MAX_TIME
            self.speed     = self.dir*1000000*self.stepSize/self.step_time/self.stepRes
            print('*** Warning *** maximum step time reached, speed reduced to ',
                  self.speed, self.stepUnit, '/s')
            print('    to lower speed, increase step resolution')
        if not silent:
            print('    Speed set to : ', self.speed, self.stepUnit, '/s')
        # if motor stopped, first empty pwm state machine FIFO
        if not self.running:
            self.pwm_sm.exec("pull(noblock)")
            self.pwm_sm.exec("pull(noblock)")
            self.pwm_sm.exec("pull(noblock)")
            self.pwm_sm.exec("pull(noblock)")
        # feed FIFO with new step duration value
        self.pwm_sm.put(self.step_time*10)

    def getSpeed(self):
        return self.speed*self.dir

    def goto(self, newpos):
        ''' go to pos (mm) '''
        pos = self.getPosition()
        nsteps = int((newpos-pos)*self.stepRes/self.stepSize)
        self.doSteps(nsteps)
