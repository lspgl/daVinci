from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ..tools.stylesheet import StyleSheet
from ..tools.colors import Colors as _C

from .subSpaces import electrodePanel
from .. import interactions
from .. import elements


class AddrLabel(QLabel):

    def __init__(self, parent, geometry):
        # Inherit from label
        QLabel.__init__(self, parent)
        self.gridPosition = 0
        self.setGeometry(geometry)
        self.parent = parent
        # self.setContentsMargins(100, 100, 100, 100)
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
                                                 function=None,
                                                 fargs=['core.spaces.runLabel'])
        self.line.setFocus()

        self.adr_in_switch = elements.StateLabelText(self, 'ADDR-IN')
        self.adr_out_switch = elements.StateLabelText(self, 'ADDR-OUT')
        self.adr_in_switch.move(self.width() - self.adr_in_switch.width() - 25, 70)
        self.adr_out_switch.move(self.width() - self.adr_out_switch.width() - 25, 50)

        self.psu_det = QLabel(self)
        self.psu_det.setText('No PSU detected')
        s = ("color:" + _C.textgray + '; font-weight: 100;'
             )
        self.psu_det.style = StyleSheet(s)
        self.psu_det.setStyleSheet(self.psu_det.style.get())
        self.psu_det.move(25, 100)

        self.current_adr = QLabel(self)
        self.current_adr.setText('No Address set')
        s = ("color:" + _C.textgray + '; font-weight: 100;'
             )
        self.current_adr.style = StyleSheet(s)
        self.current_adr.setStyleSheet(self.current_adr.style.get())
        self.current_adr.move(25, 125)

        self.delimiter = elements.Delimiter(self)
        self.delimiter.move(25, self.height() - 1)
