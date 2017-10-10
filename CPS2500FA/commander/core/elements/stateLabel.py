from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ..tools.stylesheet import StyleSheet
from ..tools.hoverListener import mouseoverEvent
from ..tools.colors import getColor
from ..tools.colors import Colors as _C


class StateLabel(QLabel):
    # Label to indicated system readyness state

    def __init__(self, parent, color=_C.highlight):
        # Inherit from label
        QLabel.__init__(self, parent)

        self.enabled = False
        self.parent = parent

        self.color = color
        self.setGeometry(QRect(0, 0, 15, 15))

        # Initialize Style
        s = ("border: 2px solid;" +
             "background-color: " + getColor(self.parent) + ";" +
             "border-radius:3px;" +
             "border-color:" + _C.textgray + ";")
        self.style = StyleSheet(s)
        self.setStyleSheet(self.style.get())

    def enable(self):
        self.style.set(background_color=self.color, border_color=self.color)
        self.setStyleSheet(self.style.get())
        self.enabled = True

    def disable(self):
        self.style.set(background_color=getColor(self.parent), border_color=_C.textgray)
        self.setStyleSheet(self.style.get())
        self.enabled = False

    def flash(self):
        self.enable()
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.disable)
        self.timer.start()
