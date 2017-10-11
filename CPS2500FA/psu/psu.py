from . import controller, digital, rs485
from .toolkit.colors import Colors as _C
from .toolkit.commandDB import CommandDB as DB
import time
from multiprocessing import Process


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
        self.state = self.gpio.state
        self.adr = None

    def stateDigital(self):
        state = self.gpio.update()
        return state

    def read_value(self, key, verbose=False, autowipe=True, **kwargs):
        entry = self.entries[key]
        if verbose == 'v' or verbose == 'vv':
            print(_C.CYAN + entry['desc'] + ': ' + _C.ENDC, end='')
        if verbose == 'vv':
            vv = True
        else:
            vv = False
        if entry['data'] is None:
            payload = self.serial.send_and_recieve(adr=self.adr,
                                                   cmd=key,
                                                   verbose=vv,
                                                   autowipe=autowipe)
        elif not isinstance(entry['data'], str) and not isinstance(entry['data'], list):
            payload = self.serial.send_and_recieve(adr=self.adr,
                                                   cmd=key,
                                                   data=entry['data'],
                                                   length=entry['length'],
                                                   verbose=vv,
                                                   autowipe=autowipe)
        else:
            if 'data' in kwargs:
                payload = self.serial.send_and_recieve(adr=self.adr,
                                                       cmd=key,
                                                       data=kwargs['data'],
                                                       length=entry['length'],
                                                       verbose=vv,
                                                       autowipe=autowipe)
            else:
                print(_C.RED + 'Missing data keyword for ' + str(hex(key)) + _C.ENDC)
                return
        if payload is None:
            return
        output = self.formatting_function(key, entry, payload)
        if verbose:
            print(_C.LIME + output + _C.ENDC)
        return(payload, entry)

    def cache_value(self, key, verbose=False, **kwargs):
        entry = self.entries[key]
        # print(_C.CYAN + 'Caching: ' + entry['desc'] + _C.ENDC)
        if entry['data'] is None:
            self.serial.send_and_forget(adr=self.adr,
                                        cmd=key,
                                        verbose=verbose)
        elif not isinstance(entry['data'], str) and not isinstance(entry['data'], list):
            self.serial.send_and_forget(adr=self.adr,
                                        cmd=key,
                                        data=entry['data'],
                                        length=entry['length'],
                                        verbose=verbose)
        else:
            if 'data' in kwargs:
                self.serial.send_and_forget(adr=self.adr,
                                            cmd=key,
                                            data=kwargs['data'],
                                            length=entry['length'],
                                            verbose=verbose)
            else:
                print(_C.RED + 'Missing data keyword for ' + str(hex(key)) + _C.ENDC)
        return

    def test(self):
        for key in self.db.readkeys:
            self.read_value(key, verbose='v', autowipe=False)
        # for e in self.c.cache[1]:
        #    print(e)

    def cachePhysics(self):
        for key in self.db.physkeys:
            self.cache_value(key, verbose=False)
        occured = []
        uniqueCache = []
        for e in reversed(self.c.cache[1]):
            cmd = e[2]['cmd']
            if cmd not in occured:
                uniqueCache.append(e)
            occured.append(cmd)
        self.c.cache[1] = uniqueCache[::-1]

    def deviceInfo(self):
        print(self.db.devicekeys)
        info = {hex(key): hex(self.read_value(key, verbose=False, autowipe=True)
                              [0]['data']) for key in self.db.devicekeys}
        return info

    def set_Addr(self, adr, verbose=False):
        self.adr = adr
        # Open Address channel
        self.gpio.listenAddr(verbose=verbose)
        # Setting Addr and closing channel
        self.serial.setAddr(adr, verbose=verbose)
        self.gpio.closeAddr(verbose=verbose)

    def reset_Addr(self, verbose=False):
        self.adr = None
        # self.gpio.listenAddr(verbose=verbose)
        self.serial.resetAddr(verbose=verbose)
        # self.gpio.closeAddr(verbose=verbose)

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
                binary = bin(data)[2:].zfill(entry['rvl'] * 8)
                integer = int(binary[:integer_res], 2)
                frac = int(binary[integer_res:], 2)
                frac = frac / 10**len(str(frac))
                value = integer + frac
            else:
                scale = 2**(entry['rvl'] * 8) - 1
                value = data / scale
            if 'maxval' in entry:
                value *= entry['maxval']
            output = str(value) + ' ' + entry['unit']
        elif key == 0x16:
            output = bin(data)[2:].zfill(entry['rvl'] * 8)
        else:
            output = data
        return str(output)

    def getCache(self):
        cache2 = self.c.cache[1]
        outputs = {}
        for e in cache2:
            key = e[2]['cmd']
            if key in self.entries:
                entry = self.entries[key]
                payload = e[2]
                output = self.formatting_function(key, entry, payload)
                outputs[key] = output
            else:
                outputs[key] = e[2]
                print('Unknown Return:')
                print(e[0])
        for key in self.db.physkeys:
            if key not in outputs:
                outputs[key] = '-'
        return outputs
