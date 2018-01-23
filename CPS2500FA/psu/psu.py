# from . import controller, digital, rs485
from .toolkit.colors import Colors as _C
from .toolkit.commandDB import CommandDB as DB
# from .toolkit import psuSignal
from .toolkit.errormask import Masks as _M
import time
from functools import wraps

import os
import sys
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
sys.path.append(__location__ + '/../')

# from controller import controller, digital, rs485
from controller.toolkit import psuSignal


class PSU:

    def __init__(self, ctrl, adr, waitForConn=False):
        """
        Main power supply class handling a single unit.

        Parameters
        ----------
        waitForConn: bool
            Waiting for Tinkerforge controller to be plugged in
        """
        self.db = DB()
        self.entries = self.db.db
        self.c = ctrl
        self.gpio = ctrl.gpio
        self.serial = ctrl.serial
        self.gpio.update()
        self.state = self.gpio.state
        self.adr = adr
        self.psu_connected = self.queryConnection()
        self.engaged = False

        self.testing = False
        self.PSUType = 'CPS2500'

        if self.PSUType == 'CPS3800':
            self.imax = 100.0  # Maximal current limit
            self.vmax = 55.0  # Maximal voltage limit
            self.vmax_ret = 60.0  # Maximal voltage readback
            self.vmin = 9.0
        elif self.PSUType == 'CPS2500':
            self.imax = 66.0  # Maximal current limit
            self.vmax = 40.0  # Maximal voltage limit
            self.vmax_ret = 48.0  # Maximal voltage readback
            self.vmin = 5.0
        else:
            raise Exception('NO PSU TYPE')

    def _requiresPSU(func):
        """
        Decorator to require a connected power supply.
        If no power supply is connected a message is shown and the function is not executed.
        Connectivity is established during the setAddr method.

        Parameters
        ----------
        func: function
            Function which has the requirement

        Returns
        -------
        func or None
            func is returned if the power supply is connected, otherwise None
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.psu_connected:
                return func(self, *args, **kwargs)
            else:
                if not self.testing:
                    print(_C.RED + _C.BOLD + 'No PSU connected' + _C.ENDC)
                    print(_C.RED + 'Required for: ' + func.__name__ + _C.ENDC)
                return None
        return wrapper

    @_requiresPSU
    def read_value(self, key, verbose=False, autowipe=True, **kwargs):
        """
        Generic value reader from the command databse

        Parameters
        ----------
        key: int
            command number as specified in the interface spec
        verbose: bool, optional
            print all rs485 signals human readable
        autowipe: bool, optional
            wipe the cache after the value is collected

        Returns
        -------
        payload: dict
            Dictionary with 'adr', 'cmd', 'data' and 'crc' keys which carry
            the response from the power supply over RS485-2.
        entry: dict
            Dictionary entry from the command database of the executed command.
        """
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
                print(_C.RED + 'Missing data keyword for ' +
                      str(hex(key)) + _C.ENDC)
                return
        if payload is None:
            return
        output = self.formatting_function(key, entry, payload)
        if verbose:
            print(_C.LIME + output + _C.ENDC)
        return(payload, entry)

    @_requiresPSU
    def cache_value(self, key, verbose=False, **kwargs):
        """
        Generic value reader from the command databse.
        Function does not wait for the value to be returned.
        The value is written to the cache through a threadsafe callback
        and can be querried from the cache at a later point.

        Parameters
        ----------
        key: int
            command number as specified in the interface spec
        verbose: bool, optional
            print all rs485 signals human readable
        """
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
                print(_C.RED + 'Missing data keyword for ' +
                      str(hex(key)) + _C.ENDC)
        return

    @_requiresPSU
    def setVoltage(self, voltage, verbose=False, getTime=False):
        """
        Set a voltage setpoint over RS485-1

        Parameters
        ----------
        voltage: float
            voltage in V to which the setpoint is set
        verbose: bool, optional
            print all rs485 signals human readable
        getTime: bool, optional
            return the response time of the command

        Returns
        -------
        v_ret: float
            voltage response from RS485-1 in V
        time: float, optional
            response time. Only in getTime is true
        """
        if not (isinstance(voltage, float) or isinstance(voltage, int)):
            print(_C.RED + 'Invalid voltage setpoint' + _C.ENDC)
            return
        if voltage > self.vmax:
            print(_C.RED + 'Voltage setpoint cant be larger than ' +
                  str(self.vmax) + 'V' + _C.ENDC)
            return
        if voltage < self.vmin:
            print(_C.RED + 'Voltage setpoint has to be larger than ' +
                  str(self.vmin) + 'V' + _C.ENDC)
            return
        # print(_C.CYAN + '⚡⚡⚡ Voltage setpoint @ ' + str(round(voltage, 2)) + 'V ⚡⚡⚡' + _C.ENDC)
        v_data = int((float(voltage) / self.vmax) * 65535)
        if not getTime:
            v_ret_data = self.serial.voltage_and_recieve(self.adr, v_data)
        else:
            v_ret_data, t = self.serial.voltage_and_recieve(
                self.adr, v_data, getTime=getTime)
        try:
            v_ret = v_ret_data['voltage'] / 65535 * self.vmax_ret
        except TypeError:
            v_ret = None
        # print(_C.YEL + '⚡⚡⚡ True voltage @ ' + str(round(v_ret, 2)) + 'V ⚡⚡⚡' + _C.ENDC)
        if not getTime:
            return v_ret
        else:
            return v_ret, t

    @_requiresPSU
    def getOn(self, verbose=False):
        """
        Query the ON/OFF state of the power supply

        Parameters
        ----------
        verbose: bool, optional
            print all rs485 signals human readable

        Returns
        -------
        engaged: bool
            True if the power supply is turned on, False if off
        """
        signal = self.serial.send_and_recieve(
            self.adr, 0x00, data=None, length=0, verbose=verbose)
        if signal['data'] == 1:
            if verbose:
                print(_C.LIME + 'Power supply turned on' + _C.ENDC)
            self.engaged = True
        else:
            if verbose:
                print(_C.RED + 'Power supply turned off' + _C.ENDC)
            self.engaged = False
        # self.write2(adr=adr, cmd=0x00, data=None, length=0, verbose=verbose)
        if verbose:
            print('')
        return self.engaged

    @_requiresPSU
    def turnOff(self, verbose=False):
        """
        Turn the power supply off

        Parameters
        ----------
        verbose: bool, optional
            print all rs485 signals human readable

        Returns
        -------
        int
            0 if the unit turned off without error, error code otherwise
        """
        if verbose:
            print(_C.BOLD + _C.YEL + '----- Turning off ----' + _C.ENDC)
        self.setCurrentLimit(current=0, verbose=verbose)

        # self.gpio.disable(1, verbose=verbose)
        # self.gpio.disable(2, verbose=verbose)

        signal = self.serial.send_and_recieve(
            adr=self.adr, cmd=0x01, data=0x0811, length=2, verbose=verbose)
        retval = signal['data']
        if retval != 0:
            if verbose:
                print(_C.RED + 'Error in turn off signal: ' +
                      str(retval) + _C.ENDC)
        else:
            if verbose:
                print(_C.LIME + 'Turn off signal OK' + _C.ENDC)

        self.getOn(verbose=verbose)
        if verbose:
            print(_C.BOLD + _C.YEL + '----------------------' + _C.ENDC)
        if retval == 0 and not self.engaged:
            return retval
        return retval

    @_requiresPSU
    def turnOn(self, verbose=False):
        """
        Turn the power supply on

        Parameters
        ----------
        verbose: bool, optional
            print all rs485 signals human readable

        Returns
        -------
        int
            0 if the unit turned on without error, error code otherwise
        """
        # Enable digital inputs
        # self.gpio.enable(1, verbose=verbose)
        # self.gpio.enable(2, verbose=verbose)
        """
        print('')
        print('SETTING VOLTAGE LIMIT T+0')
        self.serial.voltage_and_recieve(self.adr, voltage=10)
        """
        if verbose:
            print(_C.BOLD + _C.CYAN + '----- Turning on -----' + _C.ENDC)
        signal = self.serial.send_and_recieve(
            self.adr, 0x02, data=0x55AA, length=2, verbose=verbose)
        retval = signal['data']
        if verbose:
            if retval != 0:
                print(_C.RED + 'Error in turn on signal: ' +
                      str(retval) + _C.ENDC)
            else:
                print(_C.LIME + 'Turn on signal OK' + _C.ENDC)
        self.getOn(verbose=verbose)
        if verbose:
            print(_C.BOLD + _C.CYAN + '----------------------' + _C.ENDC)
        if retval == 0 and self.engaged:
            return retval
        return retval

    @_requiresPSU
    def setCurrentLimit(self, current, verbose=False):
        """
        Set the current limit of the power supply

        Parameters
        ----------
        current: float
            current limit in A
        verbose: bool, optional
            print all rs485 signals human readable

        Returns
        -------
        int
            0 if the limit is set without error, error code otherwise
        """
        if not (isinstance(current, float) or isinstance(current, int)):
            print('Invalid current limit')
            return
        if current > self.imax:
            print('Current Limit cant be larger than ' + str(self.imax) + 'A')
            return
        if current < 0:
            print('Current limit has to be larger than 0')
            return
        if verbose:
            print(_C.BLUE + 'Setting current limit to ' +
                  str(current) + 'A' + _C.ENDC)
        limit_data = int((float(current) / self.imax) * 65535)
        signal = self.serial.send_and_recieve(
            self.adr, 0x04, data=limit_data, length=2, verbose=verbose, timeout=50)
        retval = signal['data']
        return retval

    @_requiresPSU
    def getCurrentLimit(self, verbose=False):
        """
        Get the current limit of the power supply

        Parameters
        ----------
        verbose: bool, optional
            print all rs485 signals human readable

        Returns
        -------
        retval: float
            current limit in A
        """
        signal = self.serial.send_and_recieve(self.adr, 0x03, verbose=verbose)
        current = signal['data'] / 65535 * self.imax
        if verbose:
            print(_C.BLUE + 'Current limit at ' +
                  str(round(current, 2)) + 'A' + _C.ENDC)
        return current

    @_requiresPSU
    def getPhysics(self, verbose=False):
        """
        Get the physically measurable values from the power supply

        Parameters
        ----------
        verbose: bool, optional
            print all rs485 signals human readable

        Returns
        -------
        phys: dict
            Dictionary with a tuple for each property: (value, cmd)
            The dictionary is indexed with a human readable key:
            'vout': output voltage
            'iout': output current
            'pout': output power
            'vin': input voltage
            'fin': input frequency
            'temp': temperature
        """
        phys_hex = {}
        for key in self.db.physkeys:
            value = self.read_value(key, verbose=False, autowipe=True)
            if value is not None:
                data = value[0]['data']
            else:
                data = None
            phys_hex[key] = data

        phys = {'vout': (psuSignal.fullByteToDec(phys_hex[0x10], 48), 0x10),
                'iout': (psuSignal.fullByteToDec(phys_hex[0x11], 84), 0x11),
                'pout': (psuSignal.fullByteToDec(phys_hex[0x12], 3168), 0x12),
                'vin': (psuSignal.splitByteToDec(phys_hex[0x13]), 0x13),
                'fin': (psuSignal.splitByteToDec(phys_hex[0x14]), 0x14),
                'temp': (psuSignal.splitByteToDec(phys_hex[0x15]), 0x15)}

        if verbose:
            print(_C.CYAN + _C.BOLD + 'Physical values' + _C.ENDC)
            for key in phys:
                print(_C.BLUE + self.entries[phys[key][1]]['desc'] + ': ' +
                      str(round(phys[key][0], 2)) + self.entries[phys[key][1]]['unit'] + _C.ENDC)
        return phys

    @_requiresPSU
    def getError(self, verbose=False):
        """
        Get the error mask
        If an error is in the mask, the type of the error
        is looked up in errormask.py and printed

        Parameters
        ----------
        verbose: bool, optional
            print all rs485 signals human readable

        Returns
        -------
        err: str
            16bit binary error mask, MSB first
        """
        if verbose:
            print(_C.CYAN + _C.BOLD + 'Error mask' + _C.ENDC)
        payload = self.serial.send_and_recieve(adr=self.adr, cmd=0x16)
        err = format(payload['data'], '016b')[::-1]
        if '1' in err:
            for i, e in enumerate(err):
                if e == '1':
                    if verbose:
                        print(_C.RED + 'Error: ' + _M.error[i] + _C.ENDC)
        else:
            if verbose:
                print(_C.LIME + 'No errors' + _C.ENDC)
        return err

    @_requiresPSU
    def getWarning(self, verbose=False):
        """
        Get the error mask
        If an error is in the mask, the type of the error
        is looked up in errormask.py and printed

        Parameters
        ----------
        verbose: bool, optional
            print all rs485 signals human readable

        Returns
        -------
        err: str
            16bit binary error mask, MSB first
        """
        if verbose:
            print(_C.CYAN + _C.BOLD + 'Warning mask' + _C.ENDC)
        payload = self.serial.send_and_recieve(adr=self.adr, cmd=0x25)
        warn = format(payload['data'], '016b')[::-1]
        if '1' in warn:
            for i, w in enumerate(warn):
                if w == '1':
                    if verbose:
                        print(_C.RED + 'Warning: ' + _M.warning[i] + _C.ENDC)
        else:
            if verbose:
                print(_C.LIME + 'No warning' + _C.ENDC)
        return warn

    @_requiresPSU
    def clearError(self, verbose=False):
        """
        Clear the error mask

        Parameters
        ----------
        verbose: bool, optional
            print all rs485 signals human readable

        Returns
        -------
        retval: int
            0 if cleared successfull, otherwise error code
        """
        if verbose:
            print(_C.CYAN + _C.BOLD + 'Clearing error mask' + _C.ENDC)
        payload = self.serial.send_and_recieve(adr=self.adr,
                                               cmd=0x17)
        retval = payload['data']
        if verbose:
            if retval != 0:
                print(_C.RED + 'Error in mask clearing: ' +
                      _M.retcode[retval] + _C.ENDC)
            else:
                print(_C.LIME + 'Error mask cleared' + _C.ENDC)
        return retval

    @_requiresPSU
    def clearWarning(self, verbose=False):
        """
        Clear the warning mask

        Parameters
        ----------
        verbose: bool, optional
            print all rs485 signals human readable

        Returns
        -------
        retval: int
            0 if cleared successfull, otherwise error code
        """
        if verbose:
            print(_C.CYAN + _C.BOLD + 'Clearing warning mask' + _C.ENDC)
        payload = self.serial.send_and_recieve(adr=self.adr,
                                               cmd=0x26)
        retval = payload['data']
        if verbose:
            if retval != 0:
                print(_C.RED + 'Error in mask clearing: ' +
                      _M.retcode[retval] + _C.ENDC)
            else:
                print(_C.LIME + 'Warning mask cleared' + _C.ENDC)
        return retval

    @_requiresPSU
    def deviceInfo(self, verbose=False):
        """
        Get the hardware info of the device

        Parameters
        ----------
        verbose: bool, optional
            print all rs485 signals human readable

        Returns
        -------
        info: dict
            dictionary indexed with the command key and the returned entry as value
        """
        info = {key: self.read_value(key, verbose=verbose, autowipe=True)
                [0]['data'] for key in self.db.devicekeys}
        if verbose:
            print(_C.CYAN + _C.BOLD + 'Device info' + _C.ENDC)
        for key in info:
            if info[key] is not None:
                info[key] = hex(info[key])
            if verbose:
                print(
                    _C.BLUE + self.entries[key]['desc'] + ': ' + str(info[key]) + _C.ENDC)
        return info

    @_requiresPSU
    def setMaster(self, verbose=False):
        signal = self.serial.send_and_recieve(
            self.adr, 0x24, data=0x01, length=1, verbose=verbose)
        return signal

    @_requiresPSU
    def setSlave(self, verbose=False):
        signal = self.serial.send_and_recieve(
            self.adr, 0x24, data=0x00, length=1, verbose=verbose)
        return signal

    def queryConnection(self, verbose=False):
        signal = self.serial.send_and_recieve(
            self.adr, 0x00, data=None, length=0, verbose=verbose)
        if signal['adr'] is None:
            if verbose:
                print(_C.RED + 'Power supply on address ' +
                      str(self.adr) + ' not found' + _C.ENDC)
            self.psu_connected = False
            return False
        else:
            self.psu_connected = True
            return True

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

    def __str__(self):
        retstr = 'Power Supply Object on address: ' + str(self.adr)
        return retstr
