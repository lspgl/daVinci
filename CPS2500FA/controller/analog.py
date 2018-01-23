from .crc8 import crc8
import array
import time
from .toolkit.colors import Colors as _C
from .toolkit import psuSignal
import struct


class Analog:

    def __init__(self, controller):
        self.controller = controller
        self.resistance = 0.835

    def getVC(self):
        v = self.controller.vc.get_voltage() / 1000.0
        print(self.controller.vc.get_identity)
        c = v / self.resistance
        c_meas = self.controller.vc.get_current()
        # i = u/r
        print('V:', v)
        print('A:', c)
        print('A_mean:', c_meas)

        return (v, c)
