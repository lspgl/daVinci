from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ..tools.stylesheet import StyleSheet
from ..tools.colors import Colors as _C

from .subSpaces import electrodePanel
from .. import interactions
from .. import elements

import time


class HardwareLabel(QLabel):

    def __init__(self, parent, geometry):
        # Inherit from label
        QLabel.__init__(self, parent)
        self.gridPosition = 0
        self.setGeometry(geometry)
        self.parent = parent
        self.setAlignment(Qt.AlignRight)
        s = ('background-color: none; font-weight: 100; color:' + _C.textgray + ';')
        self.style = StyleSheet(s)
        self.setStyleSheet(self.style.get())
        self.setText('Power board version: -\nControl board version: -\nFirmware version: -\nSerial number: -')

    def setInfo(self, info):
        self.setText('Power board version: ' + info['0x18'] + ' \nControl board version: ' +
                     info['0x19'] + '\nFirmware version: ' + info['0x1a'] + '\nSerial number: ' + info['0x1b'])
