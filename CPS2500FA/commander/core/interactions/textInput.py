from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ..tools.stylesheet import StyleSheet
from ..tools.colors import Colors as _C
from ..tools.colors import getColor


class TextInput(QLineEdit):

    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        self.setAttribute(Qt.WA_MacShowFocusRect, 0)

        s = (
            'background-color:' + getColor(parent) + ';' +
            'color: ' + _C.textgray + ';' +
            'font-size: 15px;'
            'font-family: "Roboto";'
            'border: 0px solid black;' +
            'border-bottom: 1px solid' + _C.highlight + ';'
        )
        self.style = StyleSheet(s)

        self.setStyleSheet(self.style.get())

    def setNumericString(self):
        #reg_ex = QRegExp("^[0-9]*$")
        reg_ex = QRegExp("^[0-9]\d*(\.\d+)?$")
        self.setValidator(QRegExpValidator(reg_ex, self))
