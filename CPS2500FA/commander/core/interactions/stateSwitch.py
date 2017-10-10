from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ..tools.stylesheet import StyleSheet
from ..tools.hoverListener import mouseoverEvent
from ..tools.colors import getColor
from ..tools.colors import Colors as _C


class StateSwitch(QLabel):
    # Label to indicated system readyness state

    def __init__(self, parent, color=_C.highlight, inactive=False):
        # Inherit from label
        QLabel.__init__(self, parent)
        self.inactive = inactive
        self.enabled = False
        self.parent = parent

        self.color = color
        self.setGeometry(QRect(0, 0, 30, 15))

        self.slider = QLabel(self)
        self.slider.setGeometry(QRect(3, 3, 9, 9))
        # Initialize Style
        s = ("border: 2px solid;" +
             "background-color: " + getColor(self.parent) + ";" +
             "border-radius:7px;" +
             "border-color:" + _C.textgray + ";")
        self.style = StyleSheet(s)
        self.setStyleSheet(self.style.get())

        s_slider = ("border: 0px solid;" +
                    "background-color: " + _C.textgray + ";" +
                    "border-radius:4px;")
        self.style_slider = StyleSheet(s_slider)
        self.slider.setStyleSheet(self.style_slider.get())
        if not self.enabled:
            self.mouseReleaseEvent = self.enable
        else:
            self.mouseReleaseEvent = self.disable

    def enable(self, e=None):
        self.style_slider.set(background_color=self.color)
        self.slider.setStyleSheet(self.style_slider.get())
        self.slider.move(self.width() - self.slider.width() - 3, 3)
        self.mouseReleaseEvent = self.disable
        self.enabled = True

    def disable(self, e=None):
        self.style_slider.set(background_color=_C.textgray)
        self.slider.setStyleSheet(self.style_slider.get())
        self.slider.move(3, 3)
        self.mouseReleaseEvent = self.enable
        self.enabled = False

    def flash(self):
        self.enable()
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.disable)
        self.timer.start()

    def deactivate(self, e=None):
        self.style_slider.set(background_color=_C.lightgray)
        self.style.set(border_color=_C.lightgray)
        self.slider.setStyleSheet(self.style_slider.get())
        self.setStyleSheet(self.style.get())
        self.mouseReleaseEvent = None

    def activate(self, e=None):
        if self.enabled:
            self.mouseReleaseEvent = self.disable
            self.style_slider.set(background_color=self.color)
        else:
            self.mouseReleaseEvent = self.enable
            self.style_slider.set(background_color=_C.textgray)
        self.style.set(border_color=_C.textgray)
        self.slider.setStyleSheet(self.style_slider.get())
        self.setStyleSheet(self.style.get())
