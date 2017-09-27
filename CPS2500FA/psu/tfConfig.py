from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_io16 import BrickletIO16
from tinkerforge.bricklet_rs485 import BrickletRS485


class Controller():

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

    def connect(self):
        self.ipcon.connect(self.HOST, self.PORT)

    def disconnect(self):
        self.ipcon.disconnect()
