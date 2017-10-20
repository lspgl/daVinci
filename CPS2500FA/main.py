from psu import PSU
from psu.test import Test
from commander.application import App

if __name__ == '__main__':
    unit = PSU()

    # app = App(unit)

    Test(unit)
    # unit.cachePhysics()
