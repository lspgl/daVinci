from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ..tools.stylesheet import StyleSheet
from ..tools.hoverListener import mouseoverEvent
from ..tools.colors import getColor
from ..tools.colors import Colors as _C

from .stateLabel import StateLabel


class StateLabelText(QLabel):
    # Label to indicated system readyness state

    def __init__(self, parent, text, color=_C.highlight, width=100):
        # Inherit from label
        QLabel.__init__(self, parent)
        self.parent = parent
        self.setGeometry(QRect(0, 0, width, 15))
        self.box = StateLabel(self, color=color)

        # self.box.setGeometry(QRect(self.width() - self.box.width(), 0, self.box.width(), self.box.height()))
        self.box.move(self.width() - self.box.width(), 0)

        self.txt = QLabel(self)
        s = ("color:" + _C.textgray + ";"
             )
        self.style = StyleSheet(s)
        self.setStyleSheet(self.style.get())
        self.txt.setGeometry(QRect(0, 0, width - self.box.width(), 15))
        self.txt.setText(text)
