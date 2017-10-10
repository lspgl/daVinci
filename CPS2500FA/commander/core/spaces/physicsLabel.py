from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ..tools.stylesheet import StyleSheet
from ..tools.colors import Colors as _C

from .subSpaces import electrodePanel
from .. import interactions
from .. import elements

import time


class PhysicsLabel(QLabel):

    def __init__(self, parent, geometry):
        # Inherit from label
        QLabel.__init__(self, parent)
        self.gridPosition = 0
        self.setGeometry(geometry)
        self.move(self.x() + 25, self.y() + 25)
        self.parent = parent
        self.setAlignment(Qt.AlignTop)
        s = ('background-color: none; font-weight: 100; color:' + _C.textgray + ';')
        self.style = StyleSheet(s)
        self.setStyleSheet(self.style.get())
        self.setText('Current limit setpoint : -\n\n' +
                     'Output voltage: -\n' +
                     'Output current: -\n' +
                     'Output power: -\n\n' +
                     'Input voltage: -\n' +
                     'Input frequency: -\n' +
                     'Temperature: -\n')

        self.delimiter = elements.Delimiter(self)
        self.delimiter.move(0, self.height() - 1)

    def update(self, cache):
        self.setText('Current limit setpoint : ' + cache['0x03'] + '\n\n' +
                     'Output voltage: ' + cache['0x03'] + '\n' +
                     'Output current: ' + cache['0x03'] + '\n' +
                     'Output power: ' + cache['0x03'] + '\n\n' +
                     'Input voltage: ' + cache['0x03'] + '\n' +
                     'Input frequency: ' + cache['0x03'] + '\n' +
                     'Temperature: ' + cache['0x03'] + '\n')
