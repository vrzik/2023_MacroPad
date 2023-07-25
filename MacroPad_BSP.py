import board
import neopixel
import time
import pwmio
import busio
import terminalio
import displayio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from adafruit_st7789 import ST7789
from digitalio import DigitalInOut, Direction, Pull


class BSP():
    ####################################################################################################
    # CONSTANTS                                                                                        #
    ####################################################################################################
    
    ####################################################################################################
    # VARIABLES                                                                                        #
    ####################################################################################################
    
    ###### PINS  ########################################################################
    _NeoLED     = board.GP18
    
    _D_SCL      = board.GP10
    _D_SDA      = board.GP11
    _D_DC       = board.GP9
    _D_CS       = board.GP13
    _D_RST      = board.GP12
    _D_BLK      = board.GP14
    
    _BE_A       = board.GP5
    _BE_B       = board.GP4
    _BE_S       = board.GP3
    
    _SE_A       = board.GP6
    _SE_B       = board.GP7
    _SE_S       = board.GP8
    
    _K_R0       = DigitalInOut(board.GP15)
    _K_R1       = DigitalInOut(board.GP16)
    _K_R2       = DigitalInOut(board.GP17)
    _K_R3       = DigitalInOut(board.GP19)
    _K_C0       = DigitalInOut(board.GP20)
    _K_C1       = DigitalInOut(board.GP21)
    _K_C2       = DigitalInOut(board.GP22)
    
    LEDs        = None
    Display     = None
    __DBLK      = None
    __DSPI      = None
    
    __ACol      = 0
    
    __KeyBuffer = 0
    
    def __init__(self):
        self.LEDs = neopixel.NeoPixel(self._NeoLED, 20, brightness=0.5, auto_write = False)
        self.LEDs.fill( (0, 0, 0) )
        self.LEDs.show()
        
        self.__DBLK = pwmio.PWMOut(self._D_BLK, frequency = 1000, duty_cycle = 0)
        
        displayio.release_displays()
    
        self.__DSPI = busio.SPI(clock = self._D_SCL, MOSI = self._D_SDA)
        DisplayBus = displayio.FourWire(self.__DSPI, command = self._D_DC, chip_select = self._D_CS,
                                        reset = self._D_RST)
        self.Display = ST7789(DisplayBus, width = 280, height = 240, rowstart = 20, rotation = 90)
        
        self._K_R0.direction = Direction.INPUT
        self._K_R0.pull = Pull.DOWN
        self._K_R1.direction = Direction.INPUT
        self._K_R1.pull = Pull.DOWN
        self._K_R2.direction = Direction.INPUT
        self._K_R2.pull = Pull.DOWN
        self._K_R3.direction = Direction.INPUT
        self._K_R3.pull = Pull.DOWN
        self._K_C0.direction = Direction.OUTPUT
        self._K_C1.direction = Direction.OUTPUT
        self._K_C2.direction = Direction.OUTPUT
        
    def Periodic(self):
        bf = 0
        if self._K_R0.value:
            bf |= 1
        if self._K_R1.value:
            bf |= 8
        if self._K_R2.value:
            bf |= 64
        if self._K_R3.value:
            bf |= 512
        mask = 585
        mask = mask << self.__ACol
        bf = bf << self.__ACol
            
        self.__KeyBuffer = self.__KeyBuffer & ~mask
        self.__KeyBuffer = self.__KeyBuffer | bf
        
        if self.__ACol == 0:
            self._K_C2.value = False
        elif self.__ACol == 1:
            self._K_C1.value = False
        elif self.__ACol == 2:
            self._K_C0.value = False
        
        self.__ACol += 1
        if self.__ACol == 3:
           self.__ACol = 0
           
        if self.__ACol == 0:
            self._K_C2.value = True
        elif self.__ACol == 1:
            self._K_C1.value = True
        elif self.__ACol == 2:
            self._K_C0.value = True
            
        
    
    @property
    def DispBrightness(self):
        return int(self.__DBLK.duty_cycle / 655.35) - 1
        
    @DispBrightness.setter    
    def DispBrightness(self, Percent):
        calc = Percent * 655.35
        self.__DBLK.duty_cycle = int(calc)
        
    @property
    def KeysStatus(self):
        return self.__KeyBuffer
        
if __name__ == '__main__':
    print("BSP executed")
    MacroPad = BSP()
    
    for i in range(20):
        MacroPad.LEDs.fill( (0,0,0) )
        MacroPad.LEDs[i] = (255, (i * 30), 0)
        MacroPad.LEDs.show()
        MacroPad.DispBrightness = i * 5
        time.sleep(0.05)
        
    for i in range(19, 0, -1):
        MacroPad.LEDs.fill( (0,0,0) )
        MacroPad.LEDs[i] = ((i / 20), 0, 255)
        MacroPad.LEDs.show()
        time.sleep(0.05)
    
    for i in range(20):
        MacroPad.LEDs[i] = ( 20 + (i / 12), 250 - (i * 12), 30)
    MacroPad.LEDs.show()
    
    time.sleep(5)
    
    MacroPad.LEDs.fill( (0,0,0) )
    MacroPad.LEDs.show()
    MacroPad.DispBrightness = 0
    
    while True:
        MacroPad.Periodic()
        MacroPad.LEDs.fill( (0,0,0) )
        if MacroPad.KeysStatus != 0:
            for i in range(12):
                msk = 1 << i
                if (MacroPad.KeysStatus & msk) == msk:
                    MacroPad.LEDs[i] = ( 255, 0, 0)
        MacroPad.LEDs.show()
            
    