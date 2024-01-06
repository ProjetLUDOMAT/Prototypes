#########################################################################################
#
#   Driver for quadrature encoder
#
#########################################################################################
#
from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from math import inf
from array import array
import micropython

micropython.alloc_emergency_exception_buf(300)

# TIMEOUT   = const(0x10000)      # 65536us
TIMEOUT   = const(0x40000)      # 4 x 65536us
PIO0_BASE = const(0x50200000)   # PIO0 base address
RXF0_FIFO = const(0x20)         # RX FIFO offset
#
#   Assembler function to read FIFO_RX buffer
#
@micropython.asm_thumb
def read_fifo(r0):
    ldr(r1, [r0, 0])       # PIO0 base address -> r1
    ldr(r3, [r1, 0])       # read RX FIFO  -> r3 (r3=-1 if timeout)
    ldr(r2, [r0, 4])       # TIMEOUT -> r2
    sub(r2, r2, r3)        # r2 = TIMEOUT - r3 (r2 = TIMEOUT+1 if timeout)
    str(r2, [r0, 16])      # store pulse timing
    ldr(r2, [r1, 0])       # read RX FIFO  -> r2
    add(r3, 1)             # result = 0 if timeout
    cmp(r3, 0)             # 
    beq(END)               # if timeout, count is unchanged
    ldr(r3, [r0, 8])       # bit mask 0x1 -> r3
    and_(r2, r3)           # r2 &= r3
    str(r2, [r0, 12])      # store direction (1=forward, 0=reverse)
    ldr(r3, [r0, 20])      # count -> r3
    cmp(r2, 1)             # eq if forward      
    beq(FWD)
    sub(r2, r2, 1)         # else reverse: 0-1 -> r2
    label(FWD)
    add(r3, r3, r2)        # inc or dec r3
    str(r3, [r0, 20])      # r3 -> count
    label(END)
#
#   PIO state machine program
#
@asm_pio()
def encoder_prog():
    label("pin1_rising")               # détection d'un front montant sur pin1
    mov(isr, x)                        # TIMEOUT - x = temps en us entre 2 pulses
    mov(x, osr)                        # x chargé à TIMEOUT
    push(noblock)
    mov(isr, pins)                     # sens de rotation
    push(noblock)
    irq(noblock, rel(0))
    label("pin1_h")                    # boucle pin1 = 1
    jmp(x_dec, "pin1_h_x_not0")        # | x-- : si x s'annule, timeoout,
    jmp("pin1_rising")                 # |       dan s ce cas, reinitialisation
    label("pin1_h_x_not0")             # |       sinon
    nop()                              # |       longueur de boucle = 3 instructions
    jmp(pin, "pin1_h")                 # |       si pin1=1, on reste dans la boucle
    label("pin1_l")                    # boucle pin1 = 0
    jmp(x_dec, "pin1_l_x_not0")        # | x-- : si x s'annule, timeoout,,
    jmp("pin1_rising")                 # |       dans ce cas, reinitialisation
    label("pin1_l_x_not0")             # |       sinon
    jmp(pin, "pin1_rising")            # |       pin1=1 : fin de la période
    jmp("pin1_l")                      # |       pin1=0, on reste dans la boucle

class encoder():

    def __init__(self, sm_id=0, pin1=0, pin2=1, ppr=225, max_speed=inf):

        self.pin1      = Pin(pin1, Pin.IN, pull=None)
        self.pin2      = Pin(pin2, Pin.IN, pull=None)
        self.ppr       = ppr           # nb of pulses/rotation
        self.max_speed = max_speed
        self.speed     = 0
        self.count     = 0
        self.ar        = array('I', [PIO0_BASE + RXF0_FIFO + 0x4*sm_id, TIMEOUT, 0x1, 0, TIMEOUT, 0])
        # initialisation de la state machine: x décrémenté toutes les 3
        # instructions, donc toutes les us si freq = 3 MHz
        self._sm = StateMachine(sm_id, encoder_prog, freq=3_000_000,
                                 jmp_pin=self.pin1, in_base=self.pin2)
        self._sm.put(TIMEOUT)
        self._sm.exec("pull()")                 # TIMEOUT -> osr
        self._sm.exec("mov(x, osr)")            # TIMEOUT -> x
        while self._sm.rx_fifo():self._sm.get() # vidage du buffer fifo
        self._sm.irq(self.irq, hard=True)
        self._sm.active(True)

    def irq(self, sm):
        read_fifo(self.ar)
    
    def get_speed(self):
        if self.ar[4] == TIMEOUT + 1:
            self.speed = 0
        else:
            speed = 1e6/self.ppr/self.ar[4]
            if speed < self.max_speed:
                self.speed = speed if self.ar[3] else -speed
            # else self.speed unchanged
        return self.speed
    
    def get_count(self):
        self.count = self.ar[5] if self.ar[5] < 0x7fffffff else self.ar[5] - 0x100000000
        return self.count

    def reset_count(self):
        self.ar[5] = 0
        self.count = 0