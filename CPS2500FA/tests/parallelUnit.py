import os
import sys
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
sys.path.append(__location__ + '/../')

from controller import Controller
from network import Network
from psu import PSU
from psu.toolkit.commandDB import CommandDB
from toolkit.colors import Colors as _C
import time
import numpy as np


class ParallelUnit:

    def __init__(self, adr1=0x01, adr2=0x02):
        self.c = Controller()
        # self.n = Network(self.c)
        self.adr1 = adr1
        self.adr2 = adr2
        self.adrs = [self.adr1, self.adr2]
        self.cdb = CommandDB()

        self.checks = {}

    def test(self):
        self.checks['initializing'] = self.initializing()
        for i, psu in enumerate(self.psus):
            self.checks['setpoint_' + str(i)] = self.setpoint(psu)
            self.checks['physics_' + str(i)] = self.physics(psu)
            self.checks['device_' + str(i)] = self.device(psu)
            # self.checks['pulldown_' + str(i)] = self.pulldown(psu)
            # self.checks['multicasting_' + str(i)] = self.multicasting(psu)
            self.checks['voltage_' + str(i)] = self.voltage(psu)
        # self.checks['errorWarn_' + str(i)] = self.errorWarn(psu)

        self.format_checks(self.checks)

    def initializing(self):
        print()
        print(_C.BLUE + 'Initialization Test' + _C.ENDC)
        tests = {}
        x5_pre = self.c.stateDigital()['ADDR-OUT']
        success = False
        tries = 0
        while not success:
            self.c.resetAddr()
            self.c.listenAdr()
            self.c.setAddr(self.adr1)
            self.c.setAddr(self.adr2)
            x5_post = self.c.stateDigital()['ADDR-OUT']
            try:
                self.psu1 = PSU(self.c, self.adr1)
                self.psu1.testing = True
                self.psu2 = PSU(self.c, self.adr2)
                self.psu2.testing = True
                if self.psu1.psu_connected and self.psu2.psu_connected:
                    success = True
                else:
                    del self.psu1
                    del self.psu2
            except KeyboardInterrupt:
                sys.exit()
            except:
                pass
            tries += 1
        print(_C.YEL + 'Connection attempts: ' + str(tries) + _C.ENDC)
        self.psus = [self.psu1, self.psu2]
        if not x5_pre and x5_post:
            print(_C.LIME + 'ADDR-OUT Signaling: PASS' + _C.ENDC)
            tests['ADDR-OUT Signaling'] = True
        else:
            print(_C.RED + 'ADDR-OUT Signaling: FAIL' + _C.ENDC)
            tests['ADDR-OUT Signaling'] = False

        if self.psu1.psu_connected and self.psu2.psu_connected:
            print(_C.LIME + 'Addressing: PASS' + _C.ENDC)
            tests['Addressing'] = True
        else:
            print(_C.RED + 'Adressing: FAIL' + _C.ENDC)
            tests['Addressing'] = False
        return tests

    def setpoint(self, psu):
        print()
        print(_C.BLUE + 'Setpoint Test' + _C.ENDC)
        tests = {}
        aSet = 10
        a0 = psu.getCurrentLimit()
        print(a0)
        setpoint = psu.setCurrentLimit(aSet)
        print(setpoint)
        a1 = psu.getCurrentLimit()
        print(a1)

        psu.setCurrentLimit(0)

        if a0 is not None:
            print(_C.LIME + 'Current setpoint read: PASS' + _C.ENDC)
            tests['Current setpoint read'] = (True, a0)
        else:
            print(_C.RED + 'Current setpoint read: FAIL' + _C.ENDC)
            tests['Current setpoint read'] = (False, a0)

        if setpoint == 0:
            print(_C.LIME + 'Current setpoint write: PASS' + _C.ENDC)
            tests['Current setpoint write'] = (True, 0)
        else:
            print(_C.RED + 'Current setpoint write: FAIL' + _C.ENDC)
            tests['Current setpoint write'] = (False, setpoint)

        if isinstance(a1, float) and a1 > aSet * 0.99 and a1 < aSet * 1.01:
            print(_C.LIME + 'Current setpoint accuracy: PASS' + _C.ENDC)
            tests['Current setpoint value'] = (True, 1 - a1 / aSet)
        elif isinstance(a1, float):
            print(_C.RED + 'Current setpoint accuracy: FAIL' + _C.ENDC)
            tests['Current setpoint accuracy'] = (False, 1 - a1 / aSet)
        else:
            print(_C.RED + 'Current setpoint accuracy: FAIL' + _C.ENDC)
            tests['Current setpoint accuracy'] = (False, None)
        return tests

    def physics(self, psu):
        print()
        print(_C.BLUE + 'Physics Test' + _C.ENDC)
        tests = {}
        phys = psu.getPhysics()
        if phys is not None:
            for key in phys:
                val, cmd = phys[key]
                if val is None:
                    print(_C.RED + self.cdb.db[cmd]['desc'] +
                          '(' + str(hex(cmd)) + '): FAIL' + _C.ENDC)
                    tests[self.cdb.db[cmd]['desc'] +
                          '(' + str(hex(cmd)) + ')'] = (False, val)
                else:
                    print(_C.LIME + self.cdb.db[cmd]['desc'] +
                          ' (' + str(hex(cmd)) + '): PASS' + _C.ENDC)
                    tests[self.cdb.db[cmd]['desc'] +
                          ' (' + str(hex(cmd)) + ')'] = (True, val)
        else:
            for key in self.cdb.physkeys:
                print(_C.RED + self.cdb.db[key]['desc'] +
                      ' (' + str(hex(key)) + '): FAIL' + _C.ENDC)
                tests[self.cdb.db[key]['desc'] +
                      ' (' + str(hex(key)) + ')'] = (False, None)
        return tests

    def errorWarn(self):
        print()
        print(_C.BLUE + 'Error/Warning Test' + _C.ENDC)
        tests = {}
        nok0 = self.c.stateDigital()['MAINS-NOK']
        cycle_success = False
        if nok0:
            print(_C.YEL + _C.BOLD + 'Turn supply off and back on' + _C.ENDC)
            t0 = time.time()
            timeout = 0
            timeout_FLAG = False
            off = False

            while True:
                t1 = time.time() - t0
                print(_C.YEL + '    Timeout: ' + _C.MAGENTA +
                      str(round(timeout - t1, 1)) + _C.ENDC, end='\r')
                nok1 = self.c.stateDigital()['MAINS-NOK']
                if off and nok1:
                    cycle_success = True
                    break
                if not nok1:
                    off = True
                if t1 > timeout:
                    timeout_FLAG = True
                    break
            if timeout_FLAG:
                input(_C.YEL + _C.BOLD +
                      'Turn power supply back on and press [ENTER]\n' + _C.ENDC)
        if cycle_success:
            print(_C.LIME + 'Mains NOK signal: PASS' + _C.ENDC)
            tests['Mains NOK signal'] = True
        else:
            print(_C.RED + 'Mains NOK signal: FAIL' + _C.ENDC)
            tests['Mains NOK signal'] = False

        e1 = self.psu.getError()
        w1 = self.psu.getWarning()
        if e1 == '0000000010000000' or e1 == '0000000000000000':
            print(_C.LIME + 'Error mask read: PASS' + _C.ENDC)
            tests['Error mask read'] = True
        else:
            print(_C.RED + 'Error mask read: FAIL' + _C.ENDC)
            tests['Error mask read'] = False
        if w1 == '0000000000000000':
            print(_C.LIME + 'Warning mask read: PASS' + _C.ENDC)
            tests['Warning mask read'] = True
        else:
            print(_C.RED + 'Error mask read: FAIL' + _C.ENDC)
            tests['Warning mask read'] = False

        clearE = self.psu.clearError()
        clearW = self.psu.clearWarning()

        if clearE == 0:
            print(_C.LIME + 'Error clear: PASS' + _C.ENDC)
            tests['Error clear'] = True
        else:
            print(_C.RED + 'Error clear: FAIL' + _C.ENDC)
            tests['Error clear'] = False

        if clearW == 0:
            print(_C.LIME + 'Warning clear: PASS' + _C.ENDC)
            tests['Warning clear'] = True
        else:
            print(_C.RED + 'Warning clear: FAIL' + _C.ENDC)
            tests['Warning clear'] = False
        return tests

    def device(self, psu):
        print()
        print(_C.BLUE + 'Device Info Test' + _C.ENDC)
        info = psu.deviceInfo()
        tests = {}
        keys = self.cdb.devicekeys
        for key in keys:
            if info is None or info[key] is None:
                color = _C.RED
                success = False
                word = 'FAIL'
            else:
                color = _C.LIME
                success = True
                word = 'PASS'
            print(color + self.cdb.db[key]['desc'] + ': ' + word + _C.ENDC)
            tests[self.cdb.db[key]['desc']] = (success, info[key])
        return tests

    def pulldown(self):
        print()
        print(_C.BLUE + 'Pull-down Test' + _C.ENDC)
        print(_C.YEL + 'Not Implemented' + _C.ENDC)
        tests = {}
        return tests

    def multicasting(self, psu):
        print()
        print(_C.BLUE + 'Multicasting Test' + _C.ENDC)
        tests = {}
        master = psu.setMaster()
        slave = psu.setSlave()
        if master is not None and master['data'] == 1:
            print(_C.LIME + 'Setting master: PASS' + _C.ENDC)
            tests['Setting master'] = True
        else:
            print(_C.RED + 'Setting master: FAIL' + _C.ENDC)
            tests['Setting master'] = False
        if slave is not None and slave['data'] == 0:
            print(_C.LIME + 'Setting slave: PASS' + _C.ENDC)
            tests['Setting slave'] = True
        else:
            print(_C.RED + 'Setting slave: FAIL' + _C.ENDC)
            tests['Setting slave'] = False
        return tests

    def voltage(self, psu):
        print()
        print(_C.BLUE + 'Voltage Test' + _C.ENDC)
        tests = {}
        for i in [1, 2]:
            pre = self.c.enableSingle(i)
            post = self.c.disableSingle(i)

            if pre and post:
                print(_C.LIME + 'Enable ' + str(i) + ': PASS' + _C.ENDC)
                tests['Enable ' + str(i)] = True
            else:
                print(_C.RED + 'Enable ' + str(i) + ': FAIL' + _C.ENDC)
                tests['Enable ' + str(i)] = False
        self.c.enable()
        psu.setCurrentLimit(10)
        offstate = psu.getOn()
        turnOn = psu.turnOn()
        onstate = psu.getOn()
        voltages = []
        voltages_phys = []
        v_ref = 10
        print(_C.YEL + '⚡⚡⚡ Warning: Device voltage enabled' + _C.ENDC,
              end='\r')
        for _ in range(5):
            setvoltage = psu.setVoltage(v_ref)
            print(setvoltage)
            voltages.append(setvoltage)
            try:
                voltages_phys.append(psu.getPhysics()['vout'])
            except TypeError:
                voltages_phys.append(None)
            time.sleep(0.1)
        psu.setVoltage(0)

        turnOff = psu.turnOff()
        offstate2 = psu.getOn()
        print(' ' * 50, end='\r')
        self.c.disable()
        print(voltages)
        print(voltages_phys)
        if None in voltages:
            voltage_command_fail = True
            voltage_value_fail = True
        else:
            voltage_command_fail = False
            voltage_value_fail = False
        if None in voltages_phys:
            voltage_phys_fail = True
        else:
            voltage_phys_fail = False

        if not voltage_command_fail:
            for v in voltages:
                if abs(v - v_ref) > v_ref * 0.1:
                    voltage_value_fail = True
                    break
        if not voltage_phys_fail:
            for v in voltages_phys:
                if abs(v[0] - v_ref) > v_ref * 0.1:
                    voltage_phys_fail = True
                    break

        if offstate == 0:
            print(_C.LIME + 'Reading on-state: PASS' + _C.ENDC)
            tests['Reading on-state'] = True
        else:
            print(_C.RED + 'Reading on-state: FAIL' + _C.ENDC)
            tests['Reading on-state'] = False

        if turnOn == 0 and onstate == 1:
            print(_C.LIME + 'Turning on: PASS' + _C.ENDC)
            tests['Turning on'] = True
        else:
            print(_C.RED + 'Turning on: FAIL' + _C.ENDC)
            tests['Turning on'] = False

        if turnOff == 0 and offstate2 == 0:
            print(_C.LIME + 'Turning off: PASS' + _C.ENDC)
            tests['Turning off'] = True
        else:
            print(_C.RED + 'Turning off: FAIL' + _C.ENDC)
            tests['Turning off'] = False

        if not voltage_command_fail:
            print(_C.LIME + 'Voltage command: PASS' + _C.ENDC)
            tests['Voltage command'] = True
        else:
            print(_C.RED + 'Voltage command: FAIL' + _C.ENDC)
            tests['Voltage command'] = False

        if not voltage_value_fail:
            print(_C.LIME + 'Voltage RS485-1 value: PASS' + _C.ENDC)
            tests['Voltage RS485-1 value'] = True
        else:
            print(_C.RED + 'Voltage RS485-1 value: FAIL' + _C.ENDC)
            tests['Voltage RS485-1 value'] = False

        if not voltage_phys_fail:
            print(_C.LIME + 'Voltage RS485-2 value: PASS' + _C.ENDC)
            tests['Voltage RS485-2 value'] = True
        else:
            print(_C.RED + 'Voltage RS485-2 value: FAIL' + _C.ENDC)
            tests['Voltage RS485-2 value'] = False

        return tests

    def format_checks(self, checks):
        outstr = ''
        for key in checks:
            outstr += key + '\n'
            # print(key)
            for subkey in checks[key]:
                outstr += '    '
                outstr += subkey + ': ' + str(checks[key][subkey]) + '\n'

            outstr += '\n'

        outstr = outstr.replace('True', 'PASS').replace('False', 'FAIL')
        nfails = outstr.count('FAIL')
        npass = outstr.count('PASS')
        ntests = nfails + npass
        outstr += 'Passed ' + str(npass) + ' out of ' + \
            str(ntests) + ' test cases.'
        with open('test_log.txt', 'w') as f:
            f.write(outstr)


if __name__ == '__main__':
    u = ParallelUnit()
    u.test()
