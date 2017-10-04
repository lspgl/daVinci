from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ..tools.stylesheet import StyleSheet
from ..tools.colors import getColor
from ..tools.colors import Colors as _C


class Delimiter(QLabel):
    # Label to indicated system readyness state

    def __init__(self, parent, color=_C.highlight):
        # Inherit from label
        QLabel.__init__(self, parent)
        self.parent = parent
        self.color = color
        self.setGeometry(QRect(0, 0, self.parent.width() - 50, 1))

        # Initialize Style
        s = ("background-color: " + color + ";")
        self.style = StyleSheet(s)
        self.setStyleSheet(self.style.get())
