from psu import PSU
from psu import test
from controller import Controller
from commander.application import App

if __name__ == '__main__':
    ctrl = Controller()
    unit = PSU(ctrl)
    # app = App(unit)

    test.GeneralTest(unit)
    # test.MulticastTest(unit)
    # test.SpeedTest(unit)
    # unit.cachePhysics()
