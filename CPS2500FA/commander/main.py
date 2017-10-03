import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
# from core import core, core
from core import interactions, spaces
from core.tools.colors import Colors as _C
from core.tools.geometry import Geometry as _G


class GUI(QMainWindow):

    def __init__(self, app):
        print('Initializing GUI')
        super(GUI, self).__init__()
        self.app = app

        self.initUI()

    def initUI(self):
        # QFontDatabase.addApplicationFont("/resources/fonts/Roboto-Regular.ttf")
        # QFontDatabase.addApplicationFont("/resources/fonts/Roboto-Italic.ttf")
        # QFontDatabase.addApplicationFont("/resources/fonts/Roboto-Light.ttf")
        # QFontDatabase.addApplicationFont("/resources/fonts/Roboto-Lightitalic.ttf")

        self.setWindowTitle('CSAT')
        self.setStyleSheet("background-color:" + _C.darkgray + ";")

        self.setAutoFillBackground(True)
        self.screen = self.app.desktop().screenGeometry()

        self.mainField()
        self.windowButtons()
        self.sideBar()

        self.app.desktop().primaryScreen()
        self.showFullScreen()

        self.move(self.app.desktop().screenGeometry(1).topLeft())

    def mousePressEvent(self, event):
        focused_widget = QApplication.focusWidget()
        if isinstance(focused_widget, interactions.TextInput):
            focused_widget.clearFocus()
        QMainWindow.mousePressEvent(self, event)

    def paintEvent(self, e):

        qp = QPainter()
        qp.begin(self)

        pos = (0, 0)
        w = self.screen.width()
        h = _G.header_h
        color = _C.lightgray
        self.drawRectangles(qp, color, pos, w, h)

        pos = (0, _G.header_h + 1)
        w = _G.sidebar_w
        h = self.screen.height() - _G.header_h
        color = _C.midgray
        self.drawRectangles(qp, color, pos, w, h)

        qp.end()

    def drawRectangles(self, qp, c, pos, w, h):
        color = QColor(c)
        qp.setPen(color)
        qp.setBrush(color)
        x, y = pos
        qp.drawRect(x, y, w, h)

    def windowButtons(self):
        self.exitBtn = interactions.WindowButton(self, (self.screen.width() - 25, 10), _C.controlred)
        self.exitBtn.mouseReleaseEvent = self.exitApp

        # self.state = interactions.SateLabel(self, (45, 10), self.controlgreen, hover=False)
        # self.state.blink(self.controlred, self.controlyel)
        # self.state.steady(self.controlgreen)

    def sideBar(self):
        addrGeometry = QRect(0, _G.header_h, _G.sidebar_w, _G.addr_h)
        self.addrController = spaces.Controller(self, addrGeometry)
        self.addrController.loadSpace('core.spaces.addrLabel')

    def mainField(self):
        spaceGeometry = QRect(_G.sidebar_w, _G.header_h, self.screen.width() -
                              _G.sidebar_w, self.screen.height() - _G.header_h)
        self.contentController = spaces.Controller(self, spaceGeometry)
        self.contentController.loadSpace('core.spaces.splashLabel')
        # self.contentController.loadSpace('core.spaces.configurationLabel')

    def exitApp(self, ev=None):
        print('Closing GUI')
        self.app.quit()


def main():
    app = QApplication(sys.argv)
    w = GUI(app)
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
