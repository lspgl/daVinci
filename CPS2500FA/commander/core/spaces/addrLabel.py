from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ..tools.stylesheet import StyleSheet
from ..tools.colors import Colors as _C

from .subSpaces import electrodePanel
from .. import interactions
from .. import elements

import time


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
        self.line.setPlaceholderText('Address')
        self.line.move(25, 10)
        self.line.setFixedWidth(150)
        self.line.setNumericString()

        colors = {'main': _C.highlight, 'hover': _C.highlight,
                  'text': '#000000', 'hoverText': _C.darkgray}
        self.initBtn = interactions.ControlButton(self, (25, 50), colors, 'Initialize',
                                                  function=self.initialize,
                                                  fargs=None)
        colors = {'main': _C.controlred, 'hover': _C.controlred,
                  'text': '#000000', 'hoverText': _C.darkgray}
        self.resetBtn = interactions.ControlButton(self, (25, 90), colors, 'Reset Adr',
                                                   function=self.resetAddr,
                                                   fargs=None)
        self.line.setFocus()

        self.adr_in_switch = elements.StateLabelText(self, 'ADDR-IN')
        self.adr_out_switch = elements.StateLabelText(self, 'ADDR-OUT')
        self.mains_switch = elements.StateLabelText(self, 'MAINS-NOK', color=_C.controlred)

        self.adr_in_switch.move(self.width() - self.adr_in_switch.width() - 25, 70)
        self.adr_out_switch.move(self.width() - self.adr_out_switch.width() - 25, 50)
        self.mains_switch.move(self.width() - self.adr_out_switch.width() - 25, 90)

        self.parent.indicators.link('ADDR-IN', self.adr_in_switch)
        self.parent.indicators.link('ADDR-OUT', self.adr_out_switch)
        self.parent.indicators.link('MAINS-NOK', self.mains_switch)

        self.psu_det = QLabel(self)
        self.psu_det.setText('No PSU detected')
        s = ("color:" + _C.textgray + '; font-weight: 100;'
             )
        self.psu_det.style = StyleSheet(s)
        self.psu_det.setStyleSheet(self.psu_det.style.get())
        self.psu_det.move(25, 140)

        self.parent.text.link('STATUS', self.psu_det)

        self.current_adr = QLabel(self)
        self.current_adr.setText('No address set')
        s = ("color:" + _C.textgray + '; font-weight: 100;'
             )
        self.current_adr.style = StyleSheet(s)
        self.current_adr.setStyleSheet(self.current_adr.style.get())
        self.current_adr.move(25, 165)

        self.parent.text.link('CURRENT-ADDR', self.current_adr)

        self.delimiter = elements.Delimiter(self)
        self.delimiter.move(25, self.height() - 1)

    def initialize(self):
        if self.parent.psu.state['STATUS'] or self.parent.psu.state['STATUS'] is None:
            self.line.clear()
            self.line.setPlaceholderText('No PSU Connected')
            return
        addr_str = self.line.text()
        if addr_str == '':
            return
        if float(addr_str) > 127 or float(addr_str) == 0 or float(addr_str) != int(float(addr_str)):
            self.line.clear()
            self.line.setPlaceholderText('Invalid Address')
            return
        else:
            addr = int(addr_str, 0)
            self.line.setText(hex(addr))
            self.parent.psu.set_Addr(addr)
            info = self.parent.psu.deviceInfo()
            self.parent.controller.spaces['hardwareLabel'].setInfo(info)
            self.current_adr.setText('Address: ' + str(hex(addr)))
            self.adr_in_switch.box.flash()
            # time.sleep(1)
            # self.adr_in_switch.box.disable()

            return

    def resetAddr(self):
        if self.parent.psu.state['STATUS'] or self.parent.psu.state['STATUS'] is None:
            self.line.clear()
            self.line.setPlaceholderText('No PSU Connected')
            return

        self.line.clear()
        self.parent.psu.reset_Addr()
        self.current_adr.setText('No address set')
