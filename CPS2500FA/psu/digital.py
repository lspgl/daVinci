from .toolkit.colors import Colors as _C


class Digital:

    def __init__(self, controller):
        self.controller = controller
        self.state = {}
        keys = ['ERROR',
                'MAINS-NOK',
                'STATUS',
                'ADDR-IN',
                'ERROR485',
                'CSB+',
                'CSB-',
                'ENABLE-1',
                'ENABLE-2',
                'TRIGGER', ]

        for key in keys:
            self.state[key] = None

    def update(self):
        # Get current value from port A as bitmask
        mask_a = format(self.controller.io.get_port("a"), '08b')
        mask_b = format(self.controller.io.get_port("b"), '08b')

        self.state['STATUS'] = bool(int(mask_a[0]))
        self.state['MAINS-NOK'] = bool(int(mask_a[1]))
        self.state['ERROR'] = bool(int(mask_a[2]))

        self.state['TRIGGER'] = bool(int(mask_b[1]))
        self.state['ENABLE-2'] = bool(int(mask_b[2]))
        self.state['ENABLE-1'] = bool(int(mask_b[3]))
        self.state['CSB-'] = bool(int(mask_b[4]))
        self.state['CSB+'] = bool(int(mask_b[5]))
        self.state['ERROR485'] = bool(int(mask_b[6]))
        self.state['ADDR-IN'] = bool(int(mask_b[7]))
        # print(self.state)

        return self.state

    def listenAddr(self, verbose=False):
        if verbose:
            print(_C.BOLD + '--------------------------' + _C.ENDC)
            print(_C.BLUE + 'Opening ADDR-IN' + _C.ENDC)
        self.controller.io.set_port_configuration("b", 1 << 0, 'o', True)
        self.update()

    def closeAddr(self, verbose=False):
        if verbose:
            print(_C.BOLD + '--------------------------' + _C.ENDC)
            print(_C.BLUE + 'Closing ADDR-IN' + _C.ENDC)
        self.controller.io.set_port_configuration("b", 1 << 0, 'o', False)
        self.update()

    def status(self):
        self.update()
        print(_C.BOLD + '--------------------------' + _C.ENDC)
        print(_C.BOLD + 'CPS2500 STATUS' + _C.ENDC)
        print ('')
        if self.state['STATUS']:
            print(_C.RED + 'No PSU detected' + _C.ENDC)
        else:
            if self.state['MAINS-NOK']:
                print(_C.LIME + 'External power connected' + _C.ENDC)
            else:
                print(_C.RED + 'External power disconnected' + _C.ENDC)

            if self.state['ADDR-IN']:
                print(_C.LIME + 'Waiting for address' + _C.ENDC)
            else:
                print(_C.RED + 'Not listening for new address' + _C.ENDC)

            print ('')
            if self.state['ENABLE-1']:
                print(_C.LIME + 'Enable 1: ON' + _C.ENDC)
            else:
                print(_C.RED + 'Enable 1: OFF' + _C.ENDC)
            if self.state['ENABLE-2']:
                print(_C.LIME + 'Enable 2: ON' + _C.ENDC)
            else:
                print(_C.RED + 'Enable 2: OFF' + _C.ENDC)

            print ('')
            if self.state['ERROR']:
                print(_C.LIME + 'Error: No' + _C.ENDC)
            else:
                print(_C.RED + 'Error: Yes' + _C.ENDC)
            if self.state['ERROR485']:
                print(_C.LIME + 'RS485 Error: No' + _C.ENDC)
            else:
                print(_C.RED + 'RS485 Error: Yes' + _C.ENDC)
        print('')
