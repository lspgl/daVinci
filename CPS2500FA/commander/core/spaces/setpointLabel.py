from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ..tools.stylesheet import StyleSheet
from ..tools.colors import Colors as _C

from .subSpaces import electrodePanel
from .. import interactions
from .. import elements

import time


class SetpointLabel(QLabel):

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
        self.line.setPlaceholderText('Voltage Setpoint [V]')
        self.line.move(25, 10)
        self.line.setFixedWidth(150)
        self.line.setNumericString()

        colors = {'main': _C.highlight, 'hover': _C.highlight,
                  'text': '#000000', 'hoverText': _C.darkgray}
        self.runBtn = interactions.ControlButton(self, (25, 50), colors, 'Set Voltage',
                                                 function=self.setVoltage,
                                                 fargs=None)

        self.ready = elements.StateLabelText(self, 'Ready')
        self.ready.move(self.width() - self.ready.width() - 25, 20)

        self.enable1 = interactions.StateSwitchText(self, 'Enable I')
        self.enable2 = interactions.StateSwitchText(self, 'Enable II')
        self.enable1.move(self.width() - self.enable1.width() - 25, 50)
        self.enable2.move(self.width() - self.enable2.width() - 25, 70)

        self.engage = interactions.StateSwitchText(self, 'Engage', inactive=True)
        self.engage.move(self.width() - self.engage.width() - 25, 90)

        self.parent.indicators.link('READY', self.ready)
        self.parent.switches.link('ENABLE-1', self.enable1)
        self.parent.switches.link('ENABLE-2', self.enable2)
        self.parent.switches.link('ENGAGE', self.engage)

        # self.parent.indicators.link('ADDR-IN', self.adr_in_switch)
        # self.parent.indicators.link('ADDR-OUT', self.adr_out_switch)
        """
        self.psu_det = QLabel(self)
        self.psu_det.setText('No PSU detected')
        s = ("color:" + _C.textgray + '; font-weight: 100;'
             )
        self.psu_det.style = StyleSheet(s)
        self.psu_det.setStyleSheet(self.psu_det.style.get())
        self.psu_det.move(25, 100)

        self.parent.text.link('STATUS', self.psu_det)

        self.current_adr = QLabel(self)
        self.current_adr.setText('No address set')
        s = ("color:" + _C.textgray + '; font-weight: 100;'
             )
        self.current_adr.style = StyleSheet(s)
        self.current_adr.setStyleSheet(self.current_adr.style.get())
        self.current_adr.move(25, 125)

        self.parent.text.link('CURRENT-ADDR', self.current_adr)
        """
        self.delimiter = elements.Delimiter(self)
        self.delimiter.move(25, self.height() - 1)

    def setVoltage(self):
        if self.parent.psu.state['STATUS'] or self.parent.psu.state['STATUS'] is None:
            self.line.setText('No PSU Connected')
            return
        addr_str = self.line.text()
        if addr_str == '':
            return
        if int(addr_str, 0) > 255:
            self.line.setText('Invalid Address')
            return
        else:
            addr = int(addr_str, 0)
            self.line.setText(hex(addr))
            self.parent.psu.set_Addr(addr)
            self.current_adr.setText('Address: ' + str(hex(addr)))
            self.adr_in_switch.box.flash()
            # time.sleep(1)
            # self.adr_in_switch.box.disable()

            return

    def enable(self, i):
        pass
