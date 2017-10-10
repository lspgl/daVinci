from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ..tools.stylesheet import StyleSheet
from ..tools.hoverListener import mouseoverEvent
from ..tools.colors import getColor
from ..tools.colors import Colors as _C

from .stateSwitch import StateSwitch


class StateSwitchText(QLabel):
    # Label to indicated system readyness state

    def __init__(self, parent, text, width=100, inactive=False):
        # Inherit from label
        QLabel.__init__(self, parent)
        self.parent = parent
        self.inactive = inactive
        self.setGeometry(QRect(0, 0, width, 15))
        self.box = StateSwitch(self, inactive=self.inactive)
        if self.inactive:
            self.box.deactivate()

        # self.box.setGeometry(QRect(self.width() - self.box.width(), 0, self.box.width(), self.box.height()))
        self.box.move(self.width() - self.box.width(), 0)

        self.txt = QLabel(self)
        s = ("color:" + _C.textgray + ";"
             )
        self.style = StyleSheet(s)
        self.setStyleSheet(self.style.get())
        self.txt.setGeometry(QRect(0, 0, width - self.box.width(), 15))
        self.txt.setText(text)
