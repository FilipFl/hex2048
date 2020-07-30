from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class InfoWindow(QWidget):
    def __init__(self, path):
        super().__init__()
        self.setGeometry(500,100,343,619)
        self.setWindowTitle("Info")
        self.pixmap = QPixmap(path)
        self.label = QLabel(self)
        self.label.setPixmap(self.pixmap)
        self.show()


