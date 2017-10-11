from .core.gui import GUI
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time


class App:

    def __init__(self, psu):
        self.psu = psu
        self.app = QApplication(sys.argv)
        self.gui = GUI(self.app, self.psu, self.update)
        self.gui.show()
        sys.exit(self.app.exec_())

    def update(self, manualRS=True):
        # update Digital state
        state = self.psu.stateDigital()
        # Request new physical values to cache
        if self.psu.adr is not None and not state['STATUS'] and not manualRS:
            # self.psu.cachePhysics()
            self.gui.physics.update()
        # Address out state
        if state['ADDR-OUT']:
            self.gui.indicators.enable('ADDR-OUT')
        else:
            self.gui.indicators.disable('ADDR-OUT')

        # Power State
        if not state['MAINS-NOK']:
            self.gui.indicators.enable('MAINS-NOK')
        else:
            self.gui.indicators.disable('MAINS-NOK')

        # PSU State
        if not state['STATUS']:
            self.gui.text.setText('STATUS', 'PSU detected')
        else:
            self.gui.text.setText('STATUS', 'No PSU detected')
            self.gui.text.setText('CURRENT-ADDR', 'No address set')

        # Enable functions
        for i in [1, 2]:
            if self.gui.switches.get('ENABLE-' + str(i)):
                if not state['ENABLE-' + str(i)]:
                    self.psu.gpio.enable(i)
            else:
                if state['ENABLE-' + str(i)]:
                    self.psu.gpio.disable(i)

        if state['ENABLE-1'] and state['ENABLE-2']:
            self.gui.indicators.enable('READY')
            self.gui.switches.activate('ENGAGE')
        else:
            self.gui.indicators.disable('READY')
            self.gui.switches.deactivate('ENGAGE')
