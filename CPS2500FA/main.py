from psu import PSU
from psu import test
from commander.application import App

if __name__ == '__main__':
    unit = PSU()

    # app = App(unit)

    # test.GeneralTest(unit)
    test.SpeedTest(unit)
    # unit.cachePhysics()
