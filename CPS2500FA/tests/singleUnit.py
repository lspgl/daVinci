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


class SingleUnit:

    def __init__(self, adr=0x01):
        self.c = Controller()
        # self.n = Network(self.c)
        self.adr = adr
        self.cdb = CommandDB()

        self.checks = {}

    def test(self):
        self.checks['initializing'] = self.initializing()
        self.checks['setpoint'] = self.setpoint()
        self.checks['physics'] = self.physics()
        self.checks['device'] = self.device()
        # self.checks['pulldown'] = self.pulldown()
        self.checks['multicasting'] = self.multicasting()
        self.checks['voltage'] = self.voltage()
        self.checks['errorWarn'] = self.errorWarn(timeout=20)

        self.format_checks(self.checks)

    def initializing(self):
        print()
        print(_C.BLUE + 'Initialization Test' + _C.ENDC)
        tests = {}
        x5_pre = self.c.stateDigital()['ADDR-OUT']
        self.c.setAddr(self.adr)
        x5_post = self.c.stateDigital()['ADDR-OUT']
        self.psu = PSU(self.c, self.adr)
        self.psu.testing = True
        if not x5_pre and x5_post:
            print(_C.LIME + 'ADDR-OUT Signaling (GPIO): PASS' + _C.ENDC)
            tests['ADDR-OUT Signaling (GPIO)'] = True
        else:
            print(_C.RED + 'ADDR-OUT Signaling (GPIO): FAIL' + _C.ENDC)
            tests['ADDR-OUT Signaling (GPIO)'] = False

        if self.psu.psu_connected:
            print(_C.LIME + 'Addressing (0x05, 0x06): PASS ' + _C.ENDC)
            tests['Addressing (0x05, 0x06)'] = True
        else:
            print(_C.RED + 'Adressing (0x05, 0x06): FAIL' + _C.ENDC)
            tests['Addressing (0x05, 0x06)'] = False

        if len(failAdr) == 0:
            print(_C.LIME + 'Address space (' +
                  str(adrspace[0]) + '-' + str(adrspace[-1]) + '): PASS' + _C.ENDC)
            tests['Address space (' + str(adrspace[0]) +
                  '-' + str(adrspace[-1]) + ')'] = True
        else:
            print(_C.RED + 'Address space (' +
                  str(adrspace[0]) + '-' + str(adrspace[-1]) + '): FAIL' + _C.ENDC)
            tests['Address space (' + str(adrspace[0]) + '-' +
                  str(adrspace[-1]) + ')'] = (False, str(failAdr))
        return tests

    def setpoint(self):
        print()
        print(_C.BLUE + 'Setpoint Test' + _C.ENDC)
        tests = {}
        aSet = 10
        a0 = self.psu.getCurrentLimit()
        print(a0)
        setpoint = self.psu.setCurrentLimit(aSet)
        print(setpoint)
        a1 = self.psu.getCurrentLimit()
        print(a1)

        self.psu.setCurrentLimit(0)

        if a0 is not None:
            print(_C.LIME + 'Current setpoint read (0x03): PASS' + _C.ENDC)
            tests['Current setpoint read (0x03)'] = (True, a0)
        else:
            print(_C.RED + 'Current setpoint read (0x03): FAIL' + _C.ENDC)
            tests['Current setpoint read (0x03)'] = (False, a0)

        if setpoint == 0:
            print(_C.LIME + 'Current setpoint write (0x04): PASS' + _C.ENDC)
            tests['Current setpoint write (0x04)'] = (True, 0)
        else:
            print(_C.RED + 'Current setpoint write (0x04): FAIL' + _C.ENDC)
            tests['Current setpoint write (0x04)'] = (False, setpoint)

        if isinstance(a1, float) and a1 > aSet * 0.99 and a1 < aSet * 1.01:
            print(_C.LIME + 'Current setpoint accuracy (0x03, 0x04): PASS' + _C.ENDC)
            tests['Current setpoint value (0x03, 0x04)'] = (
                True, 1 - a1 / aSet)
        elif isinstance(a1, float):
            print(_C.RED + 'Current setpoint accuracy (0x03, 0x04): FAIL' + _C.ENDC)
            tests['Current setpoint accuracy (0x03, 0x04)'] = (
                False, 1 - a1 / aSet)
        else:
            print(_C.RED + 'Current setpoint accuracy (0x03, 0x04): FAIL' + _C.ENDC)
            tests['Current setpoint accuracy (0x03, 0x04)'] = (False, None)
        return tests

    def physics(self):
        print()
        print(_C.BLUE + 'Physics Test' + _C.ENDC)
        tests = {}
        phys = self.psu.getPhysics()
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

    def errorWarn(self, timeout=5):
        print()
        print(_C.BLUE + 'Error/Warning Test' + _C.ENDC)
        tests = {}
        nok0 = self.c.stateDigital()['MAINS-NOK']
        cycle_success = False
        if nok0:
            print(_C.YEL + _C.BOLD + 'Turn supply off and back on' + _C.ENDC)
            t0 = time.time()
            timeout = 20
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
            if timeout_FLAG and timeout != 0:
                input(_C.YEL + _C.BOLD +
                      'Turn power supply back on and press [ENTER]\n' + _C.ENDC)
        if cycle_success:
            print(_C.LIME + 'Mains NOK signal (GPIO): PASS' + _C.ENDC)
            tests['Mains NOK signal (GPIO)'] = True
        else:
            print(_C.RED + 'Mains NOK signal (GPIO): FAIL' + _C.ENDC)
            tests['Mains NOK signal (GPIO)'] = False

        e1 = self.psu.getError()
        w1 = self.psu.getWarning()
        if e1 is not None:
            print(_C.LIME + 'Error mask read (0x16): PASS' + _C.ENDC)
            tests['Error mask read (0x16)'] = True
        else:
            print(_C.RED + 'Error mask read (0x16): FAIL' + _C.ENDC)
            tests['Error mask read (0x16)'] = False
        if w1 is not None:
            print(_C.LIME + 'Warning mask read (0x25): PASS' + _C.ENDC)
            tests['Warning mask read (0x25)'] = True
        else:
            print(_C.RED + 'Warning mask read (0x25): FAIL' + _C.ENDC)
            tests['Warning mask read (0x25)'] = False

        clearE = self.psu.clearError()
        clearW = self.psu.clearWarning()
        w2 = self.psu.getWarning()
        e2 = self.psu.getError()

        if clearE == 0 and e2 == '0000000000000000':
            print(_C.LIME + 'Error clear (0x17): PASS' + _C.ENDC)
            tests['Error clear (0x17)'] = True
        else:
            print(_C.RED + 'Error clear (0x17): FAIL' + _C.ENDC)
            tests['Error clear (0x17)'] = False

        if clearW == 0 and w2 == '0000000000000000':
            print(_C.LIME + 'Warning clear (0x26): PASS' + _C.ENDC)
            tests['Warning clear (0x26)'] = True
        else:
            print(_C.RED + 'Warning clear (0x26): FAIL' + _C.ENDC)
            tests['Warning clear (0x26)'] = False
        return tests

    def device(self):
        print()
        print(_C.BLUE + 'Device Info Test' + _C.ENDC)
        info = self.psu.deviceInfo()
        tests = {}
        keys = self.cdb.devicekeys
        for key in keys:
            if info is None or info[key] is None:
                color = _C.RED
                success = False
                word = 'FAIL'
                val = None
            else:
                color = _C.LIME
                success = True
                word = 'PASS'
                val = info[key]
            print(color + self.cdb.db[key]['desc'] + ' (' +
                  str(hex(key)) + ')' + ': ' + word + _C.ENDC)
            tests[self.cdb.db[key]['desc'] +
                  ' (' + str(hex(key)) + ')'] = (success, val)
        return tests

    def pulldown(self):
        print()
        print(_C.BLUE + 'Pull-down Test' + _C.ENDC)
        print(_C.YEL + 'Not Implemented' + _C.ENDC)
        tests = {}
        return tests

    def multicasting(self):
        print()
        print(_C.BLUE + 'Multicasting Test' + _C.ENDC)
        tests = {}
        master = self.psu.setMaster()
        slave = self.psu.setSlave()
        if master is not None and master['data'] == 1:
            print(_C.LIME + 'Setting master (0x24): PASS' + _C.ENDC)
            tests['Setting master (0x24)'] = True
        else:
            print(_C.RED + 'Setting master (0x24): FAIL' + _C.ENDC)
            tests['Setting master (0x24)'] = False
        if slave is not None and slave['data'] == 0:
            print(_C.LIME + 'Setting slave (0x24): PASS' + _C.ENDC)
            tests['Setting slave (0x24)'] = True
        else:
            print(_C.RED + 'Setting slave (0x24): FAIL' + _C.ENDC)
            tests['Setting slave (0x24)'] = False
        return tests

    def voltage(self):
        print()
        print(_C.BLUE + 'Voltage Test' + _C.ENDC)
        tests = {}
        for i in [1, 2]:
            pre = self.c.enableSingle(i)
            post = self.c.disableSingle(i)

            if pre and post:
                print(_C.LIME + 'Enable ' + str(i) + ' (GPIO): PASS' + _C.ENDC)
                tests['Enable ' + str(i) + ' (GPIO)'] = True
            else:
                print(_C.RED + 'Enable ' + str(i) + ' (GPIO): FAIL' + _C.ENDC)
                tests['Enable ' + str(i) + ' (GPIO)'] = False
        self.psu.setCurrentLimit(10)
        self.c.enable()
        self.psu.setCurrentLimit(10)
        offstate = self.psu.getOn()
        turnOn = self.psu.turnOn()
        onstate = self.psu.getOn()
        voltages = []
        voltages_phys = []
        v_ref = 10
        print(_C.YEL + '⚡⚡⚡ Warning: Device voltage enabled' + _C.ENDC,
              end='\r')
        for i in range(20):
            setvoltage = self.psu.setVoltage(v_ref, verbose=False)
            voltages.append(setvoltage)
            try:
                voltage_phys = self.psu.getPhysics()
                voltages_phys.append(voltage_phys['vout'])
            except TypeError:
                voltages_phys.append(None)
            time.sleep(0.1)

        self.psu.setVoltage(0)

        turnOff = self.psu.turnOff()
        offstate2 = self.psu.getOn()
        print(' ' * 100, end='\r')
        self.c.disable()
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
            v_avg = np.mean(voltages)
            if abs(v_avg - v_ref) > v_ref * 0.1:
                voltage_value_fail = True
            # for v in voltages:
            #    if abs(v - v_ref) > v_ref * 0.1:
            #        voltage_value_fail = True
            #        break
        if not voltage_phys_fail:
            v_phys_avg = np.mean(voltages_phys)
            if abs(v_phys_avg - v_ref) > v_ref * 0.1:
                voltage_phys_fail = True
            # for v in voltages_phys:
            #    if abs(v[0] - v_ref) > v_ref * 0.1:
            #        voltage_phys_fail = True
            #        break

        if offstate == 0:
            print(_C.LIME + 'Reading on-state (0x00): PASS' + _C.ENDC)
            tests['Reading on-state (0x00)'] = True
        else:
            print(_C.RED + 'Reading on-state (0x00): FAIL' + _C.ENDC)
            tests['Reading on-state (0x00)'] = False

        if turnOn == 0 and onstate == 1:
            print(_C.LIME + 'Turning on (0x02): PASS' + _C.ENDC)
            tests['Turning on (0x02)'] = True
        else:
            print(_C.RED + 'Turning on (0x02): FAIL' + _C.ENDC)
            tests['Turning on (0x02)'] = False

        if turnOff == 0 and offstate2 == 0:
            print(_C.LIME + 'Turning off (0x01): PASS' + _C.ENDC)
            tests['Turning off (0x01)'] = True
        else:
            print(_C.RED + 'Turning off (0x01): FAIL' + _C.ENDC)
            tests['Turning off (0x01)'] = False

        if not voltage_command_fail:
            print(_C.LIME + 'Voltage command (RS485-1): PASS' + _C.ENDC)
            tests['Voltage command (RS485-1)'] = True
        else:
            print(_C.RED + 'Voltage command (RS485-1): FAIL' + _C.ENDC)
            tests['Voltage command (RS485-1)'] = False

        if not voltage_value_fail:
            print(_C.LIME + 'Voltage RS485-1 value (RS485-1): PASS' + _C.ENDC)
            tests['Voltage RS485-1 value (RS485-1)'] = True
        else:
            print(_C.RED + 'Voltage RS485-1 value (RS485-1): FAIL' + _C.ENDC)
            tests['Voltage RS485-1 value (RS485-1)'] = False

        if not voltage_phys_fail:
            print(_C.LIME + 'Voltage RS485-2 value (RS485-1, 0x10): PASS' + _C.ENDC)
            tests['Voltage RS485-2 value (RS485-1, 0x10)'] = True
        else:
            print(_C.RED + 'Voltage RS485-2 value (RS485-1, 0x10): FAIL' + _C.ENDC)
            tests['Voltage RS485-2 value (RS485-1, 0x10)'] = False

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
    u = SingleUnit()
    u.test()
