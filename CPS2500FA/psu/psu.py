from . import controller, digital, rs485
from .toolkit.colors import Colors as _C
from .toolkit.commandDB import CommandDB as DB
from .toolkit import psuSignal
from .toolkit.errormask import Masks as _M
import time
from functools import wraps


class PSU:

    def __init__(self, waitForConn=True):
        self.db = DB()
        self.entries = self.db.db
        self.c = controller.Controller()
        self.controller_connected = False
        self.psu_connected = False
        self.adr = None
        self.engaged = False

        self.imax = 66.0  # Maximal current limit
        self.vmax = 40.0  # Maximal voltage limit
        self.vmax_ret = 48.0  # Maximal voltage readback
        self.vmin = 0.0

        self.initialize()
        if waitForConn:
            if not self.controller_connected:
                print(_C.BOLD + _C.YEL + 'Please connect the Tinkerforge controller' + _C.ENDC)
                while not self.controller_connected:
                    self.initialize()
        if self.controller_connected:
            print(_C.BOLD + _C.CYAN + 'Tinkerforge controller connected')
        else:
            print(_C.BOLD + _C.RED + 'Tinkerforge controller not connected')

    def initialize(self):
        self.controller_connected = self.c.connect()
        if self.controller_connected:
            # Initialize digital and serial interfaces
            self.gpio = digital.Digital(self.c)
            self.serial = rs485.RS485(self.c)
            self.gpio.update()
            self.state = self.gpio.state
            return True
        return False

    def _requiresController(func):
        # Decorator to ensure the tinkerforge controller is connected
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.controller_connected:
                return func(self, *args, **kwargs)
            else:
                print(_C.RED + _C.BOLD + 'No controller connected' + _C.ENDC)
                print(_C.RED + 'Required for: ' + func.__name__ + _C.ENDC)
                return None
        return wrapper

    def _requiresPSU(func):
        # Decorator to ensure the power supply is connected
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.psu_connected:
                return func(self, *args, **kwargs)
            else:
                print(_C.RED + _C.BOLD + 'No PSU connected' + _C.ENDC)
                print(_C.RED + 'Required for: ' + func.__name__ + _C.ENDC)
                return None
        return wrapper

    @_requiresController
    def stateDigital(self):
        self.gpio.update()
        self.gpio.status()
        return self.gpio.state

    @_requiresPSU
    @_requiresController
    def read_value(self, key, verbose=False, autowipe=True, **kwargs):
        # Generic value reader for values in DB
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

    @_requiresPSU
    @_requiresController
    def cache_value(self, key, verbose=False, **kwargs):
        # Generic value cacher for values in db
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

    @_requiresPSU
    @_requiresController
    def setVoltage(self, voltage, verbose=False):
        if not (isinstance(voltage, float) or isinstance(voltage, int)):
            print(_C.RED + 'Invalid voltage setpoint' + _C.ENDC)
            return
        if voltage > self.vmax:
            print(_C.RED + 'Voltage setpoint cant be larger than ' + str(self.vmax) + 'V' + _C.ENDC)
            return
        if voltage < self.vmin:
            print(_C.RED + 'Voltage setpoint has to be larger than ' + str(self.vmin) + 'V' + _C.ENDC)
            return
        print(_C.CYAN + '⚡⚡⚡ Voltage setpoint @ ' + str(round(voltage, 2)) + 'V ⚡⚡⚡' + _C.ENDC)
        v_data = int((float(voltage) / self.vmax) * 65535)
        v_ret_data = self.serial.voltage_and_recieve(self.adr, v_data)
        v_ret = v_ret_data['voltage'] / 65535 * self.vmax_ret
        print(_C.YEL + '⚡⚡⚡ True voltage @ ' + str(round(v_ret, 2)) + 'V ⚡⚡⚡' + _C.ENDC)
        return v_ret

    @_requiresPSU
    @_requiresController
    def getOn(self, verbose=False):
        signal = self.serial.send_and_recieve(self.adr, 0x00, data=None, length=0, verbose=verbose)
        if signal['data'] == 1:
            print(_C.LIME + 'Power supply turned on' + _C.ENDC)
            self.engaged = True
        else:
            print(_C.RED + 'Power supply turned off' + _C.ENDC)
            self.engaged = False
        # self.write2(adr=adr, cmd=0x00, data=None, length=0, verbose=verbose)
        if verbose:
            print ('')
        return self.engaged

    @_requiresPSU
    @_requiresController
    def turnOff(self, verbose=False):
        print(_C.BOLD + _C.YEL + '----- Turning off ----' + _C.ENDC)
        limit = 0
        self.setCurrentLimit(limit, verbose=verbose)

        self.gpio.disable(1, verbose=verbose)
        self.gpio.disable(2, verbose=verbose)

        signal = self.serial.send_and_recieve(adr=self.adr, cmd=0x01, data=0x0811, length=2, verbose=verbose)
        retval = signal['data']
        if retval != 0:
            print(_C.RED + 'Error in turn off signal: ' + str(retval) + _C.ENDC)
        else:
            print(_C.LIME + 'Turn off signal OK' + _C.ENDC)

        self.getOn(verbose=verbose)
        print(_C.BOLD + _C.YEL + '----------------------' + _C.ENDC)
        if retval == 0 and not self.engaged:
            return True
        return False

    @_requiresPSU
    @_requiresController
    def turnOn(self, verbose=False):
        # Turn on sequence
        # Enable digital inputs
        self.gpio.enable(1, verbose=verbose)
        self.gpio.enable(2, verbose=verbose)
        """
        print('')
        print('SETTING VOLTAGE LIMIT T+0')
        self.serial.voltage_and_recieve(self.adr, voltage=10)
        """
        print(_C.BOLD + _C.CYAN + '----- Turning on -----' + _C.ENDC)
        signal = self.serial.send_and_recieve(self.adr, 0x02, data=0x55AA, length=2, verbose=verbose)
        retval = signal['data']
        if retval != 0:
            print(_C.RED + 'Error in turn on signal: ' + str(retval) + _C.ENDC)
        else:
            print(_C.LIME + 'Turn on signal OK' + _C.ENDC)
        self.getOn(verbose=verbose)
        print(_C.BOLD + _C.CYAN + '----------------------' + _C.ENDC)
        if retval == 0 and self.engaged:
            return True
        return False

    @_requiresPSU
    @_requiresController
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

    @_requiresPSU
    @_requiresController
    def setCurrentLimit(self, limit, verbose=False):
        if not (isinstance(limit, float) or isinstance(limit, int)):
            print('Invalid current limit')
            return
        if limit > self.imax:
            print('Current Limit cant be larger than ' + str(self.imax) + 'A')
            return
        if limit < 0:
            print('Current limit has to be larger than 0')
            return
        print(_C.BLUE + 'Setting current limit to ' + str(limit) + 'A' + _C.ENDC)
        limit_data = int((float(limit) / self.imax) * 65535)
        signal = self.serial.send_and_recieve(self.adr, 0x04, data=limit_data, length=2, verbose=verbose, timeout=50)
        retval = signal['data']
        return retval

    @_requiresPSU
    @_requiresController
    def getCurrentLimit(self, verbose=False):
        signal = self.serial.send_and_recieve(self.adr, 0x03, verbose=verbose)
        retval = signal['data'] / 65535 * self.imax
        print(_C.BLUE + 'Current limit at ' + str(round(retval, 2)) + 'A' + _C.ENDC)
        return retval

    @_requiresController
    def setAddr(self, adr, verbose=False):
        print(_C.BOLD + _C.CYAN + '---- Setting addr ----' + _C.ENDC)
        print(_C.LIME + 'Address: ' + str(hex(adr)) + _C.ENDC)
        self.adr = adr
        # Open Address channel
        self.gpio.listenAddr(verbose=verbose)
        # Setting Addr and closing channel
        self.serial.write2(adr=0x00, cmd=0x06, data=0x1234, length=2, verbose=verbose)
        self.serial.write2(adr=0x00, cmd=0x05, data=adr, length=1, verbose=verbose)
        self.gpio.closeAddr(verbose=verbose)
        signal = self.serial.send_and_recieve(self.adr, 0x00, data=None, length=0, verbose=verbose)
        if signal is not None:
            self.psu_connected = True
        else:
            self.adr = None
            print(_C.RED + 'Address failure: No PSU detected')
        print(_C.BOLD + _C.CYAN + '----------------------' + _C.ENDC)

    @_requiresController
    def resetAddr(self, verbose=False):
        # Resetting the device address of all devices in the domain
        self.adr = None
        self.serial.write2(adr=0x00, cmd=0x06, data=0x1234, length=2, verbose=verbose)
        signal = self.serial.send_and_recieve(self.adr, 0x00, data=None, length=0, verbose=verbose)
        if signal is None:
            self.psu_connected = False

    @_requiresPSU
    @_requiresController
    def getPhysics(self, verbose=False):
        phys_hex = {key: self.read_value(key, verbose=False, autowipe=True)
                    [0]['data'] for key in self.db.physkeys}

        phys = {'vout': (psuSignal.fullByteToDec(phys_hex[0x10], 48), 0x10),
                'iout': (psuSignal.fullByteToDec(phys_hex[0x11], 84), 0x11),
                'pout': (psuSignal.fullByteToDec(phys_hex[0x12], 4032), 0x12),
                'vin': (psuSignal.splitByteToDec(phys_hex[0x13]), 0x13),
                'fin': (psuSignal.splitByteToDec(phys_hex[0x14]), 0x14),
                'temp': (psuSignal.splitByteToDec(phys_hex[0x15]), 0x15)}

        print(_C.CYAN + _C.BOLD + 'Physical values' + _C.ENDC)
        for key in phys:
            print(_C.BLUE + self.entries[phys[key][1]]['desc'] + ': ' +
                  str(round(phys[key][0], 2)) + self.entries[phys[key][1]]['unit'] + _C.ENDC)
        return phys

    @_requiresPSU
    @_requiresController
    def getError(self, verbose=False):
        print(_C.CYAN + _C.BOLD + 'Error mask' + _C.ENDC)
        payload = self.serial.send_and_recieve(adr=self.adr, cmd=0x16)
        err = format(payload['data'], '016b')[::-1]
        if '1' in err:
            for i, e in enumerate(err):
                if e == '1':
                    print(_C.RED + 'Error: ' + _M.error[i] + _C.ENDC)
        else:
            print(_C.LIME + 'No errors' + _C.ENDC)
        return err

    @_requiresPSU
    @_requiresController
    def clearError(self, verbose=False):
        print(_C.CYAN + _C.BOLD + 'Clearing error mask' + _C.ENDC)
        # payload = self.serial.send_and_recieve(adr=self.adr,
        #                                           cmd=0x23)
        # print(payload)
        payload = self.serial.send_and_recieve(adr=self.adr,
                                               cmd=0x17)
        retval = payload['data']
        if retval != 0:
            print(_C.RED + 'Error in mask clearing: ' + _M.retcode[retval] + _C.ENDC)
        else:
            print(_C.LIME + 'Error mask cleared' + _C.ENDC)
        return retval

    @_requiresPSU
    @_requiresController
    def deviceInfo(self):
        info = {key: hex(self.read_value(key, verbose=False, autowipe=True)
                         [0]['data']) for key in self.db.devicekeys}
        print(_C.CYAN + _C.BOLD + 'Device info' + _C.ENDC)
        for key in info:
            print(_C.BLUE + self.entries[key]['desc'] + ': ' + info[key] + _C.ENDC)
        return info

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
