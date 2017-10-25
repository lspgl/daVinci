from .crc8 import crc8
import array
import time
from .toolkit.colors import Colors as _C
from .toolkit import psuSignal
import struct


class RS485:

    def __init__(self, controller):
        self.controller = controller
        self.STX = 0x02
        self.ports = [self.controller.rs1, self.controller.rs2]
        self.deadtime = 20.0 / 1000.0

    def calc_crc(self, byte_array):
        crc_val = crc8()
        # value = ''.join(map(chr, byte_array))
        crc_val.update(bytes(byte_array))
        return crc_val.digest()

    def write1(self, adr, data, verbose=False):
        if adr is None:
            print('WARNING: No address set')
            return
        data_b = data.to_bytes(2, 'big')
        data_l = [d for d in data_b]
        send_array = [self.STX] + [adr] + data_l
        crc = ord(self.calc_crc(send_array))
        send_array += [crc]
        if verbose:
            print('')
            print('Sending', send_array)

        send_array = list(map(chr, bytes(send_array)))
        self.ports[0].write(send_array)

    def write2(self, adr, cmd, data, length, verbose=False):
        if adr is None:
            print('WARNING: No address set')
            return
        if data is not None:
            data_b = data.to_bytes(length, 'big')
            data_l = [d for d in data_b]
            send_length = len(data_l)
            # data_l = [data]
            # send_length = length

            send_array = [self.STX] + [adr] + [cmd] + [send_length] + data_l
        else:
            send_length = 0
            send_array = [self.STX] + [adr] + [cmd] + [send_length]

        crc = ord(self.calc_crc(send_array))
        send_array += [crc]
        if verbose:
            print('')
            psuSignal.tablePrint(send_array, send_length)
        # send_array = "".join(map(chr, hex(send_array)))
        send_array = list(map(chr, bytes(send_array)))
        self.ports[1].write(send_array)

    def readCache(self, cache, verbose=False, last=False):
        if verbose:
            for entry in cache:
                psuSignal.tablePrint(*entry[:2], recieving=True)

        if last:
            return cache[-1]
        else:
            return cache

    def setMulticastMaster(self, adr, verbose=False):
        signal = self.send_and_recieve(adr, 0x24, data=1, length=1, verbose=verbose)
        print(signal)
        return signal

    def voltage_and_recieve(self, adr, data, timeout=50, autowipe=True, verbose=False, getTime=False):
        cachesize_init = len(self.controller.cache[0])
        if verbose:
            print(_C.BOLD + '--------------------------' + _C.ENDC)
            print(_C.BOLD + 'Setting Voltage ' + _C.MAGENTA + str(data) + '[16 bit]' + _C.ENDC)
        self.write1(adr=adr, data=data, verbose=verbose)
        wait = 0
        t0 = time.time()
        while len(self.controller.cache[0]) == cachesize_init and wait < timeout:
            wait = (time.time() - t0) * 1000
            pass

        if wait >= timeout:
            print(_C.RED + 'Response Timeout' + _C.ENDC)
            recieved = None
            return recieved
        else:
            recieved = self.readCache(self.controller.cache[0], verbose=verbose, last=True)
            if autowipe:
                self.controller.wipeCache()
        if verbose:
            print('')
        if getTime:
            return recieved[-1], wait
        return recieved[-1]

    def send_and_recieve(self, adr, cmd, data=None, length=0, timeout=50, autowipe=True, verbose=False):
        cachesize_init = len(self.controller.cache[1])

        if verbose:
            print(_C.BOLD + '--------------------------' + _C.ENDC)
            print(_C.BOLD + 'Sending Command ' + _C.MAGENTA + str(hex(cmd)) + _C.ENDC)
        self.write2(adr=adr, cmd=cmd, data=data, length=length, verbose=verbose)
        wait = 0
        t0 = time.time()
        while len(self.controller.cache[1]) == cachesize_init and wait < timeout:
            wait = (time.time() - t0) * 1000
            pass

        if wait >= timeout:
            print(_C.RED + 'Response Timeout' + _C.ENDC)
            recieved = None
            return recieved
        else:
            recieved = self.readCache(self.controller.cache[1], verbose=verbose, last=True)
            if autowipe:
                self.controller.wipeCache()
        if verbose:
            print('')
        return recieved[-1]

    def send_and_forget(self, adr, cmd, data=None, length=0, timeout=50, verbose=False):
        if verbose:
            print(_C.BOLD + '--------------------------' + _C.ENDC)
            print(_C.BOLD + 'Sending Command ' + _C.MAGENTA + str(hex(cmd)) + _C.ENDC)
        self.write2(adr=adr, cmd=cmd, data=data, length=length, verbose=verbose)
        time.sleep(self.deadtime)
        return
