from .crc8 import crc8
import array
import time
from .toolkit.colors import Colors as _C


class RS485():

    def __init__(self, controller):
        self.controller = controller
        self.STX = 0x02
        self.ADDR = 0x00

    def cb_read(self, message):
        print('Message: "' + ''.join(message) + '"')

    def calc_crc(self, byte_array):
        crc_val = crc8()
        crc_val.update("".join(map(chr, byte_array)))
        return crc_val.digest()

    def test(self):
        self.controller.rs2.set_rs485_configuration(1250000, self.controller.rs2.PARITY_NONE, self.controller.rs2.STOPBITS_1,
                                                    self.controller.rs2.WORDLENGTH_8, self.controller.rs2.DUPLEX_HALF)

        # Register read callback to function cb_read
        self.controller.rs2.register_callback(self.controller.rs2.CALLBACK_READ, self.cb_read)

        # Enable read callback
        self.controller.rs2.enable_read_callback()

        Command = 0x00
        DATA = [0x00]

        send_length = len(DATA)
        # send_length = 0
        send_array = [self.STX] + [self.ADDR] + [Command] + [send_length] + DATA
        send_array += [ord(self.calc_crc(send_array))]

        send_array = bytes(send_array)
        print(send_array)

        self.controller.rs2.write(send_array)
        # time.sleep(1)
