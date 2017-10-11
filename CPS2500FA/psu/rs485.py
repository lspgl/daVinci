from .crc8 import crc8
import array
import time
from .toolkit.colors import Colors as _C
from .toolkit import psuSignal


class RS485:

    def __init__(self, controller):
        self.controller = controller
        self.STX = 0x02
        self.ports = [self.controller.rs1, self.controller.rs2]
        self.deadtime = 20.0 / 1000.0

    def calc_crc(self, byte_array):
        crc_val = crc8()
        crc_val.update("".join(map(chr, byte_array)))
        return crc_val.digest()

    def write(self, adr, cmd, data, length, port, verbose=False):
        if adr is None:
            print('WARNING: No address set')
            return
        if data is not None:
            data_b = data.to_bytes(length, 'big')
            data_l = [d for d in data_b]
            send_length = len(data_l)

            send_array = [self.STX] + [adr] + [cmd] + [send_length] + data_l
        else:
            send_length = 0
            send_array = [self.STX] + [adr] + [cmd] + [send_length]

        crc = ord(self.calc_crc(send_array))
        send_array += [crc]
        if verbose:
            print('')
            psuSignal.tablePrint(send_array, send_length)
        send_array = list(map(chr, bytes(send_array)))
        port.write(send_array)

    def readCache(self, cache, verbose=False, last=False):
        if verbose:
            for entry in cache:
                psuSignal.tablePrint(*entry[:2], recieving=True)

        if last:
            return cache[-1]
        else:
            return cache

    def setAddr(self, adr, verbose=False):
        if verbose:
            print(_C.BOLD + '--------------------------' + _C.ENDC)
            print(_C.BOLD + 'Setting Address to ' + _C.MAGENTA + str(hex(adr)) + _C.ENDC)
        self.write(adr=0x00, cmd=0x06, data=0x1234, length=2, port=self.ports[1], verbose=verbose)
        self.write(adr=0x00, cmd=0x05, data=adr, length=1, port=self.ports[1], verbose=verbose)
        if verbose:
            print ('')

    def resetAddr(self, verbose=False):
        if verbose:
            print(_C.BOLD + '--------------------------' + _C.ENDC)
            print(_C.BOLD + 'Resetting Address' + _C.ENDC)
        self.write(adr=0x00, cmd=0x06, data=0x1234, length=2, port=self.ports[1], verbose=verbose)
        if verbose:
            print ('')

    def send_and_recieve(self, adr, cmd, data=None, length=0, timeout=50, autowipe=True, verbose=False):
        cachesize_init = len(self.controller.cache[1])

        if verbose:
            print(_C.BOLD + '--------------------------' + _C.ENDC)
            print(_C.BOLD + 'Sending Command ' + _C.MAGENTA + str(hex(cmd)) + _C.ENDC)
        self.write(adr=adr, cmd=cmd, data=data, length=length, port=self.ports[1], verbose=verbose)
        wait = 0
        t0 = time.time()
        while len(self.controller.cache[1]) == cachesize_init and wait < timeout:
            wait = (time.time() - t0) * 1000
            pass

        if wait >= timeout:
            print(_C.RED + 'Response Timeout' + _C.ENDC)
            print('')
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
        self.write(adr=adr, cmd=cmd, data=data, length=length, port=self.ports[1], verbose=verbose)
        time.sleep(self.deadtime)
        return
