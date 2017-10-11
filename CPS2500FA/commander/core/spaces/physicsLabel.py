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

        colors = {'main': _C.highlight, 'hover': _C.highlight,
                  'text': '#000000', 'hoverText': _C.darkgray}
        self.initBtn = interactions.ControlButton(self, (0, 160), colors, 'Query Physics',
                                                  function=self.update,
                                                  fargs=None)

    def update(self):
        self.parent.psu.cachePhysics()
        cache = self.parent.psu.getCache()
        self.setText('Current limit setpoint : ' + cache[int('0x03', 0)] + '\n\n' +
                     'Output voltage: ' + cache[int('0x10', 0)] + '\n' +
                     'Output current: ' + cache[int('0x11', 0)] + '\n' +
                     'Output power: ' + cache[int('0x12', 0)] + '\n\n' +
                     'Input voltage: ' + cache[int('0x13', 0)] + '\n' +
                     'Input frequency: ' + cache[int('0x14', 0)] + '\n' +
                     'Temperature: ' + cache[int('0x15', 0)] + '\n')
