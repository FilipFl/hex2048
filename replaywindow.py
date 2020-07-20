from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from cBoard import Board
from middles import middle, offsetX, offsetY
import math


class ReplayGame:
    def __init__(self):
        self.board = Board()

    def recreate_state(self, state):
        self.board = Board()
        self.board.recreate_map(state)

    def get_block(self,x,y):
        return self.board.get_field(x,y).get_block()


class Replay(QWidget):
    def __init__(self):
        super().__init__()
        self.game = ReplayGame()
        self.setGeometry(300,300,600,600)
        self.setWindowTitle("Replay")
        self.update()
        self.show()

    def recreate(self, state):
        self.game.recreate_state(state)
        self.update()

    def hex_corner(self, center, size, i):
        angle_deg = 60 * i
        angle_rad = math.pi / 180 * angle_deg
        return QPoint(center[0] + size * math.cos(angle_rad),
                      center[1] + size * math.sin(angle_rad))

    def paintEvent(self,event):
        painter = QPainter(self)
        if self.game is not None:
            painter.setPen(QPen(Qt.black, 5, Qt.SolidLine))
            size = 30
            for element in middle:
                painter.setPen(QPen(Qt.black, 5, Qt.SolidLine))
                block = self.game.get_block(element[1][0],element[1][1])
                txt = ""
                if block is not None:
                    if block.get_player()==1:
                        painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
                        txt = block.value_to_string()
                    else:
                        painter.setBrush(QBrush(Qt.green, Qt.SolidPattern))
                        txt = block.value_to_string()
                else:
                    painter.setBrush(QBrush(Qt.black, Qt.NoBrush))
                points = [self.hex_corner(element[0],size,0),
                    self.hex_corner(element[0],size,1),
                    self.hex_corner(element[0],size,2),
                    self.hex_corner(element[0], size, 3),
                    self.hex_corner(element[0], size, 4),
                    self.hex_corner(element[0], size, 5)]
                poly = QPolygon(points)
                painter.drawPolygon(poly)
                if txt != "":
                    painter.setPen(QPen(Qt.black, 10, Qt.SolidLine))
                    painter.drawText(QRectF(element[0][0]-30, element[0][1]-10,60,20),Qt.AlignHCenter|Qt.AlignVCenter, txt)