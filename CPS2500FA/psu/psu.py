from . import controller, digital, rs485
from .toolkit.colors import Colors as _C
from .toolkit.commandDB import CommandDB as DB


class PSU:

    def __init__(self):
        self.db = DB()
        self.entries = self.db.db
        self.c = controller.Controller()
        self.c.connect()
        # Initialize digital and serial interfaces
        self.gpio = digital.Digital(self.c)
        self.serial = rs485.RS485(self.c)
        self.gpio.update()
        self.adr = None

    def read_value(self, key, verbose=False, **kwargs):
        entry = self.entries[key]
        print(_C.CYAN + entry['desc'] + ':' + _C.ENDC)
        if entry['data'] is None:
            payload = self.serial.send_and_recieve(adr=self.adr,
                                                   cmd=key,
                                                   verbose=verbose)
        elif not isinstance(entry['data'], str) and not isinstance(entry['data'], list):
            payload = self.serial.send_and_recieve(adr=self.adr,
                                                   cmd=key,
                                                   data=entry['data'],
                                                   length=entry['length'])
        else:
            if 'data' in kwargs:
                payload = self.serial.send_and_recieve(adr=self.adr,
                                                       cmd=key,
                                                       data=kwargs['data'],
                                                       length=entry['length'])
            else:
                print(_C.RED + 'Missing data keyword for ' + str(hex(key)) + _C.ENDC)
                return
        if payload is None:
            return
        text_output = self.formatting_function(key, entry, payload)
        print(_C.LIME + text_output + _C.ENDC)
        return(payload, entry)

    def test(self):
        for key in self.db.readkeys:
            self.read_value(key, verbose=False)

    def set_Addr(self, adr, verbose=False):
        self.adr = adr
        # Open Address channel
        self.gpio.listenAddr(verbose=verbose)
        # Setting Addr and closing channel
        self.serial.setAddr(adr, verbose=verbose)
        self.gpio.closeAddr(verbose=verbose)

    def clear_Error(self, verbose=False):
        payload = self.serial.send_and_recieve(adr=self.adr,
                                               cmd=0x17)
        print(payload)

    def formatting_function(self, key, entry, payload):
        data = payload['data']
        if key == 0x00:
            if data == 0:
                output = 'Off'
            else:
                output = 'On'
        elif entry['retval'] == 'phys':
            if 'res' in entry:
                integer_res = int(entry['res'])
                #frac_res = int(10 * (entry['res'] - integer))
                binary = bin(data)[2:].zfill(entry['rvl'] * 8)
                integer = int(binary[:integer_res], 2)
                frac = int(binary[integer_res:], 2)
                frac = frac / 10**len(str(frac))
                output = str(integer + frac) + ' ' + entry['unit']
            else:
                scale = 2**(entry['rvl'] * 8) - 1
                output = str(data / scale) + ' ' + entry['unit']
        elif key == 0x16:
            output = bin(data)[2:].zfill(entry['rvl'] * 8)
        else:
            output = data
        return str(output)
