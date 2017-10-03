from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ..tools.stylesheet import StyleSheet
from ..tools.colors import Colors as _C

from .subSpaces import electrodePanel
from .. import interactions


class Space(QLabel):

    def __init__(self, controller):
        # Inherit from label
        QLabel.__init__(self, controller.parent)
        self.setGeometry(controller.geometry)
        self.setContentsMargins(100, 100, 100, 100)
        self.setAlignment(Qt.AlignTop)
        s = ("background-color:" + _C.midgray + '; font-weight: 100;'
             )
        self.style = StyleSheet(s)
        self.setStyleSheet(self.style.get())

        self.line = interactions.TextInput(self)
        self.line.setPlaceholderText('Decimal Address')
        self.line.move(25, 10)
        self.line.setFixedWidth(150)
        self.line.setNumericString()

        colors = {'main': _C.highlight, 'hover': _C.highlight,
                  'text': '#000000', 'hoverText': _C.darkgray}
        self.runBtn = interactions.ControlButton(self, (25, 50), colors, 'Set Address',
                                                 function=controller.loadSpace,
                                                 fargs=['core.spaces.runLabel'])
        self.line.setFocus()
