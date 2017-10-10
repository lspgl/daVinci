from psu.psu import PSU
from commander.application import App

if __name__ == '__main__':
    unit = PSU()

    app = App(unit)

    # unit.gpio.status()
    # unit.set_Addr(0x01)
    # unit.cachePhysics()
    # unit.test()
