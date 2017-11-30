from .toolkit.colors import Colors as _C
import time
import sys


def GeneralTest(psu):
    psu.stateDigital()
    print()
    psu.setAddr(0x01)
    print()
    psu.deviceInfo()
    print()
    psu.getPhysics()
    print()
    psu.getError()
    print()
    psu.clearError()
    print()
    #input(_C.BOLD + _C.MAGENTA + "Ready for turn on [Press any key]" + _C.ENDC)
    psu.turnOn()
    print()
    psu.setCurrentLimit(current=1)
    print()
    # Voltage ramping test
    """
    psu.setVoltage(voltage=5)
    time.sleep(2)
    print()
    psu.getPhysics()
    print()
    psu.setVoltage(voltage=10)
    time.sleep(2)
    print()
    psu.getPhysics()
    print()
    psu.setVoltage(voltage=15)
    time.sleep(2)
    print()
    """
    psu.getPhysics()
    print()
    print()
    psu.getCurrentLimit()
    print()
    #input(_C.BOLD + _C.MAGENTA + "Ready for turn off [Press any key]" + _C.ENDC)
    psu.turnOff()


def SpeedTest(psu):
    import numpy as np
    times = []
    psu.setAddr(0x01)
    psu.deviceInfo()
    psu.turnOn()
    psu.setCurrentLimit(current=1)
    for i in range(1000):
        v, t = psu.setVoltage(voltage=5, getTime=True)
        times.append(t)
        # print(t)

    avg = np.mean(np.array(times))
    mx = np.max(np.array(times))
    mn = np.min(np.array(times))
    print('Average respones time:', avg)
    print('Max respones time:', mx)
    print('Min respones time:', mn)
    psu.turnOff()


def MulticastTest(psu):
    psu.stateDigital()
    print()
    psu.setAddr(0x01)
    print()
    psu.getCurrentLimit()
    print()
    psu.setMaster()
