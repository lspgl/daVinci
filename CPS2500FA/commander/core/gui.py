import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from . import interactions, spaces
from .tools.colors import Colors as _C
from .tools.geometry import Geometry as _G

from .api import indicators, text, switches, physics


class GUI(QMainWindow):

    def __init__(self, app, update_fct):
        print('Initializing GUI')
        super(GUI, self).__init__()
        self.app = app
        # Load API handles
        self.indicators = indicators.Indicators()
        self.text = text.Text()
        self.switches = switches.Switches()

        self.initUI(update_fct)

    def initUI(self, update_fct):
        # QFontDatabase.addApplicationFont("/resources/fonts/Roboto-Regular.ttf")
        # QFontDatabase.addApplicationFont("/resources/fonts/Roboto-Italic.ttf")
        # QFontDatabase.addApplicationFont("/resources/fonts/Roboto-Light.ttf")
        # QFontDatabase.addApplicationFont("/resources/fonts/Roboto-Lightitalic.ttf")

        self.controller = spaces.Controller()

        self.setWindowTitle('CSAT')
        self.setStyleSheet("background-color:" + _C.darkgray + ";")

        self.setAutoFillBackground(True)
        self.screen = self.app.desktop().screenGeometry()

        self.mainField()
        self.windowButtons()
        self.sideBar()
        self.hardwareInfo()

        self.app.desktop().primaryScreen()
        # self.showFullScreen()
        self.resize(1500, 1000)

        # self.move(self.app.desktop().screenGeometry(1).topLeft())

        self.timer = QTimer(self)
        self.timer.setInterval(50)
        # self.timer.timeout.connect(update_fct)
        self.timer.start()

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
        cursor = _G.header_h
        geometry = QRect(0, cursor, _G.sidebar_w, _G.addr_h)
        self.controller.initSpace('addrLabel', spaces.AddrLabel(self, geometry))
        cursor += self.controller.spaces['addrLabel'].height()

        geometry = QRect(0, cursor, _G.sidebar_w, _G.setpoint_h)
        self.controller.initSpace('setpointLabel', spaces.SetpointLabel(self, geometry))
        cursor += self.controller.spaces['setpointLabel'].height()

        geometry = QRect(0, cursor, _G.sidebar_w, _G.physics_h)
        self.controller.initSpace('physicsLabel', spaces.PhysicsLabel(self, geometry))
        self.physics = physics.Physics(self.controller.spaces['physicsLabel'])

    def mainField(self):
        geometry = QRect(_G.sidebar_w, _G.header_h, self.screen.width() -
                         _G.sidebar_w, self.screen.height() - _G.header_h)
        self.controller.initSpace('splashLabel', spaces.SplashLabel(self, geometry))

    def hardwareInfo(self):
        geometry = QRect(self.screen.width() - 225 + 11, 25, 200, _G.header_h - 25)
        self.controller.initSpace('hardwareLabel', spaces.HardwareLabel(self, geometry))

    def exitApp(self, ev=None):
        print('Closing GUI')
        self.app.quit()


def main():
    app = QApplication(sys.argv)
    w = GUI(app, psu)
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
