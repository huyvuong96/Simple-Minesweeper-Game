from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Button(QPushButton):
    clicked = pyqtSignal()
    r_clicked = pyqtSignal()

    def __init__(self):
        super(Button, self).__init__()

        self.setFixedSize(QSize(30, 30))
    

    def mouseReleaseEvent(self, e):

        if (e.button() == Qt.RightButton):
            self.r_clicked.emit()

        elif (e.button() == Qt.LeftButton):
            self.clicked.emit()