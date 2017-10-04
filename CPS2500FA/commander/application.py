from .gui import GUI
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

    def update(self):
        state = self.psu.gpio.update()
        # print(state)
        if state['ADDR-OUT']:
            self.gui.controller.spaces['addrLabel'].adr_out_switch.box.enable()
