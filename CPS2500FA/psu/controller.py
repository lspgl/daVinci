from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_io16 import BrickletIO16
from tinkerforge.bricklet_rs485 import BrickletRS485
from .toolkit.psuSignal import parseReturn1, parseReturn2


class Controller:

    HOST = 'localhost'
    PORT = 4223
    IO16_ID = 'CE3'
    RS485_1_ID = 'CUc'
    RS485_2_ID = 'CV6'

    def __init__(self):
        self.ipcon = IPConnection()
        self.io = BrickletIO16(self.IO16_ID, self.ipcon)
        self.rs1 = BrickletRS485(self.RS485_1_ID, self.ipcon)
        self.rs2 = BrickletRS485(self.RS485_2_ID, self.ipcon)
        self.rs485 = [self.rs1, self.rs2]

        self.cache = [[], []]
        self.callbackFn = [self.cb_read_1, self.cb_read_2]

    def cb_read_1(self, signal):
        signal = parseReturn1(signal)
        self.cache[0].append(signal)

    def cb_read_2(self, signal):
        signal = parseReturn2(signal)
        self.cache[1].append(signal)

    def wipeCache(self, which=2):
        self.cache[which - 1] = []

    def connect(self):
        self.ipcon.connect(self.HOST, self.PORT)
        for i, rs in enumerate(self.rs485):
            rs.set_rs485_configuration(1250000, rs.PARITY_NONE, rs.STOPBITS_1,
                                       rs.WORDLENGTH_8, rs.DUPLEX_HALF)
            rs.register_callback(rs.CALLBACK_READ, self.callbackFn[i])
            rs.enable_read_callback()

    def disconnect(self):
        self.ipcon.disconnect()
