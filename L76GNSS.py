from distutils.log import debug
import math
import struct
import time
from machine import Pin

class L76GNSS:
   
    ACC_I2CADDR = const(30)
    PRODUCTID_REG = const(0x0F)

    def __init__(self, pytrack = None, sda = 'P22', scl = 'P21'):
        if pytrack is not None:
            self.i2c = pytrack.i2c
        else:
            from machine import I2C
            self.i2c = I2C(0, mode=I2C.MASTER, pins=(sda, scl))

    def getCoordinates(self):
        coords = L76GNSS.coordinates(debug=False)
        return coords