from psu.psu import PSU
from commander.application import App

if __name__ == '__main__':
    unit = PSU()
    app = App(unit)
    # unit.gpio.status()
    # unit.set_Addr(0x01)
    # unit.read_value(0x00)
    # unit.gpio.status()
    # unit.test()
    # unit.clear_Error()
    # unit.test()
    # unit.gpio.status()
    # unit.read_state()
    # unit.read_setpoint()
    # unit.read_v_out()
