from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os


class SplashLabel(QLabel):

    def __init__(self, parent, geometry):
        # Inherit from label
        QLabel.__init__(self, parent)
        self.setGeometry(geometry)
        self.parent = parent

        print(self.width())
        print(self.height())
        directory = os.path.dirname(__file__)

        imageFrame = QLabel(self)
        image = QPixmap(os.path.join(directory, '../../resources/img/cpslogo.png'))
        imageFrame.setPixmap(image)

        imageFrame.move((self.width() - image.width()) / 2,
                        (self.height() - image.height()) / 2)
