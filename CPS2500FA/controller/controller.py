from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_io16 import BrickletIO16
from tinkerforge.bricklet_rs485 import BrickletRS485
from tinkerforge.brick_master import BrickMaster

from .toolkit.psuSignal import parseReturn1, parseReturn2
from .toolkit.colors import Colors as _C
import time

import sys


from . import digital
from .import rs485


class Controller:

    HOST = 'localhost'
    PORT = 4223

    def __init__(self, waitForConn=True):
        self.ipcon = IPConnection()
        self.cache = [[], []]

        self.connect()
        if waitForConn:
            if not self.connected:
                print(_C.BOLD + _C.YEL + 'Please connect the CPS Commander' + _C.ENDC)
                while not self.connected:
                    self.connect()
        if self.connected:
            print(_C.BOLD + _C.CYAN + 'CPS Commander connected' + _C.ENDC)
            self.gpio = digital.Digital(self)
            self.serial = rs485.RS485(self)
            self.gpio.update()
            self.state = self.gpio.state
        else:
            print(_C.BOLD + _C.RED + 'CPS Commander not connected' + _C.ENDC)

    def cb_read_1(self, signal):
        signal = parseReturn1(signal)
        self.cache[0].append(signal)

    def cb_read_2(self, signal):
        # print('reading:', signal)
        signal = parseReturn2(signal)
        self.cache[1].append(signal)

    def wipeCache(self, which=2):
        self.cache[which - 1] = []

    def reset(self):
        self.disconnect()
        self.connect()

    def connect(self):
        self.ipcon.connect(self.HOST, self.PORT)
        self.ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE, self.callback)
        self.connected = False
        self.ipcon.enumerate()
        time.sleep(.1)
        if self.connected:
            self.io = BrickletIO16(self.IO16_ID, self.ipcon)
            self.rs1 = BrickletRS485(self.RS485_1_ID, self.ipcon)
            self.rs2 = BrickletRS485(self.RS485_2_ID, self.ipcon)
            self.rs485 = [self.rs1, self.rs2]
            self.callbackFn = [self.cb_read_1, self.cb_read_2]
            for i, rs in enumerate(self.rs485):
                rs.set_rs485_configuration(1250000, rs.PARITY_NONE, rs.STOPBITS_1,
                                           rs.WORDLENGTH_8, rs.DUPLEX_HALF)
                rs.register_callback(rs.CALLBACK_READ, self.callbackFn[i])
                rs.enable_read_callback()
            return True
        else:
            self.ipcon.disconnect()
            return False

    def disconnect(self):
        self.ipcon.disconnect()

    def callback(self,
                 uid,
                 connected_uid,
                 position,
                 hardware_version,
                 firmware_version,
                 device_identifier,
                 enumeration_type):

        if position == 0:
            self.MASTER_ID = uid
        elif position == 'c':
            self.IO16_ID = uid
        elif position == 'b':
            self.RS485_2_ID = uid
        elif position == 'd':
            self.RS485_1_ID = uid

        self.connected = True

    def stateDigital(self, verbose=False):
        self.gpio.update()
        if verbose:
            self.gpio.status()
        return self.gpio.state

    def listenAdr(self, verbose=False):
        # Open Address channel
        self.gpio.listenAddr(verbose=verbose)
        return

    def enableSingle(self, i, verbose=False):
        self.gpio.enable(i, verbose=verbose)
        check = self.gpio.getPassthrough(i, verbose=verbose)
        return check

    def disableSingle(self, i, verbose=False):
        self.gpio.disable(i, verbose=verbose)
        check = self.gpio.getPassthrough(i, verbose=verbose)
        return (not check)

    def enable(self, verbose=False):
        e1 = self.enableSingle(1, verbose=verbose)
        e2 = self.enableSingle(2, verbose=verbose)
        check = e1 and e2
        return check

    def disable(self, verbose=False):
        d1 = self.enableSingle(1, verbose=verbose)
        d2 = self.enableSingle(2, verbose=verbose)
        check = d1 and d2
        return check

    def closeAdr(self, verbose=False):
        self.gpio.closeAddr(verbose=verbose)
        return

    def setAddr(self, adr, verbose=False):
        """
        Go through the complete addressing procedure of the power supply

        The on-state is querried immediately after the address is set to
        check for a response (if it's on or off is irrelevant) and consequently

        Parameters
        ----------
        adr: int
            address in the range 0-255
        verbose: bool, optional
            print all rs485 signals human readable

        Returns
        -------
        adr: int or None
            returns the address if successfull, otherwise None
        """
        if verbose:
            print(_C.BOLD + _C.CYAN + '---- Setting addr ----' + _C.ENDC)
            print(_C.LIME + 'Address: ' + str(hex(adr)) + _C.ENDC)

        # Setting Addr and closing channel
        self.serial.write2(adr=0x00, cmd=0x05, data=adr, length=1, verbose=verbose)
        # self.gpio.closeAddr(verbose=verbose)
        if verbose:
            print(_C.BOLD + _C.CYAN + '----------------------' + _C.ENDC)
        return True

    def resetAddr(self, verbose=False):
        """
        Reset the address of a power supply.
        If multiple supplies are connected this will reset all of them.

        Parameters
        ----------
        verbose: bool, optional
            print all rs485 signals human readable
        """
        self.serial.write2(adr=0x00, cmd=0x06, data=0x1234, length=2, verbose=verbose)
        return True
