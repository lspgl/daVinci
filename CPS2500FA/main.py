from psu import tfConfig, digital, rs485

if __name__ == '__main__':
    controller = tfConfig.Controller()
    controller.connect()
    gpio = digital.Digital(controller)

    gpio.status()
    gpio.listenAddr()
    gpio.status()
    gpio.closeAddr()
    gpio.status()

    #serial = rs485.RS485(controller)
    # serial.test()
    # gpio.status()

    controller.disconnect()
