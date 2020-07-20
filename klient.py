from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QLabel, QGraphicsScene, QGraphicsView, QMainWindow, QGraphicsPolygonItem, QGraphicsTextItem
from PySide2 import QtGui
from PySide2.QtGui import QPainter, QBrush, QPen, QPolygonF, QPolygon, QFont, QPixmap
from PySide2.QtCore import QPoint, Qt, QRectF, QPointF, QRunnable, QThreadPool, Slot, QObject,  Signal
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import random
import math
import sys
import os
import socket
import xmlrpc.client
from client import Networking_client

class WorkerSignals(QObject):
    finished = Signal()

class Worker (QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        finally:
            self.signals.finished.emit()  # Done






class Board:
    def __init__(self):
        self.map = []
        for i in range(0,9):
            row = []
            if i==0 or i==8:
                for j in range(0,5):
                    f = Field(i, j)
                    row.append(f)
            if i==1 or i==7:
                for j in range(0,6):
                    f = Field(i,j)
                    row.append(f)
            if i==2 or i==6:
                for j in range(0,7):
                    f = Field(i,j)
                    row.append(f)
            if i==3 or i==5:
                for j in range(0,8):
                    f = Field(i,j)
                    row.append(f)
            else:
                for j in range(0,9):
                    f= Field(i,j)
                    row.append(f)
            self.map.append(row)

    def get_field(self,x,y):
        return self.map[x][y]

    def recreate_map(self, state):
        for element in state:
            field = self.get_field(element[0],element[1])
            if element[2] != 0:
                field.make_block(element[2], element[3])



    # metoda co runde tworząca klocek aktualnie grającego gracza
    def create_block(self, player):
        count = 0
        for element in middle:
            x = element[1][0]
            y = element[1][1]
            possible = self.get_field(x, y).get_block()
            if possible is not None:
                count += 1
        if count != len(middle):
            done = False
            while not done:
                x = random.randint(0, 9)
                y = random.randint(0, 9)
                status, ble = self.check_bound(x,y)
                if status:
                    possible = self.get_field(x,y).get_block()
                    if possible is None:
                        self.get_field(x, y).make_block(player)
                        done = True

    def create_state(self):
        game_state = []
        for element in middle:
            block = self.get_field(element[1][0], element[1][1]).get_block()
            if block is not None:
                player = block.get_player()
                value = block.get_value()
            else:
                player = 0
                value = 0
            field = [element[1][0], element[1][1], player, value]
            game_state.append(field)
        return game_state

    def move_blocks(self,player, dir):
        blocks = []
        old_state = self.create_state()
        for column in self.map:
            for field in column:
                block = field.get_block()
                if block != None:
                    if block.get_player() == player:
                        blocks.append(block)
        # przesuwanie każdego klocka po kolei, aż nic się nie będzie zmieniać na planszy
        nothing_changed = False
        while not nothing_changed:
            # określenie które klocki powinny poruszać się najpierw, w zależności jaki kierunek ruchu
            if dir == 0:
                blocks.sort(key=lambda x: x.get_y(), reverse=True)
            if dir == 3:
                blocks.sort(key=lambda x: x.get_y())
            if dir == 2:
                blocks.sort(key=lambda x: x.get_x())
            if dir == 5:
                blocks.sort(key=lambda x: x.get_x(), reverse=True)
            if dir == 1:
                blocks.sort(key=lambda x: x.get_x())
            if dir == 4:
                blocks.sort(key=lambda x: x.get_x(), reverse=True)
            nothing_changed = True
            for item in blocks:
                old = item.get_coords()
                possible, new_coords = item.get_address_to_move(dir)
                if possible:
                    existing = self.get_field(new_coords[0], new_coords[1]).get_block()
                    if existing is not None:
                        if existing.get_player() == player and existing.get_value() == item.get_value():
                            existing.mul_value()
                            blocks.remove(item)
                            self.get_field(old[0], old[1]).del_block()
                            nothing_changed = False
                    else:
                        item.set_coords(new_coords)
                        self.get_field(new_coords[0],new_coords[1]).asign_block(item)
                        self.get_field(old[0], old[1]).del_block()
                        nothing_changed = False
        new_state = self.create_state()
        #sprawdzenie czy cokolwiek się zmieniło jeśli nie, ruch niepoprawny
        if old_state == new_state:
            return False
        else:
            return True

    # sprawdzenie czy współrzędne znajdują się na mapie
    def check_bound(self, x, y):
        if x < 0 or y < 0 or x > 8:
            return False, [x, y]
        if x < 5:
            if y - x > 4:
                return False, [x, y]
        if (x == 5 and y > 7) or (x == 6 and y > 6) or (x == 7 and y > 5) or (x == 8 and y > 4):
            return False, [x, y]
        return True, [x, y]


class Field:
    def __init__(self, x, y):
        self.pos_x = x
        self.pos_y = y
        self.blocked = None

    def make_block(self, player, value=2):
        self.blocked = Block(player, self.pos_x, self.pos_y, value)

    def del_block(self):
        self.blocked = None

    def asign_block(self, block):
        self.blocked = block

    def get_block(self):
        return self.blocked


class Block:

    def __init__(self, player, x, y, value):
        self.value = value
        self.owned_by = player
        self.x_pos = x
        self.y_pos = y

    def mul_value(self):
        self.value = self.value * 2

    def get_value(self):
        return self.value

    def get_player(self):
        return self.owned_by

    def get_coords(self):
        return [self.x_pos,self.y_pos]

    def set_coords(self, lista):
        self.x_pos = lista[0]
        self.y_pos = lista[1]

    def get_x(self):
        return self.x_pos

    def get_y(self):
        return self.y_pos

    def value_to_string(self):
        # funkcja do printowania wartości
        s = ''
        s += str(self.value)
        return s


    def get_adress_to_move(self, dir):
        # 0 - w dół
        # 1 - lewo dół
        # 2 - lewo góra
        # 3 - góra
        # 4 - prawo góra
        # 5 - prawo dół
        directions = []
        if self.x_pos < 4:
            directions = [[0,+1],[-1,0],[-1,-1],[0,-1],[+1,0],[+1,+1]]
        elif self.x_pos > 4:
            directions = [[0,+1],[-1,+1],[-1,0],[0,-1],[+1,-1],[+1,0]]
        else:
            directions = [[0,+1],[-1,0],[-1,-1],[0,-1],[+1,-1],[+1,0]]
        get_dir = directions[dir]
        new_x = get_dir[0]+self.x_pos
        new_y = get_dir[1]+self.y_pos
        if new_x<0 or new_y<0 or new_x>8:
            return False, [new_x,new_y]
        if new_x < 5:
            if new_y-new_x > 4:
                return False, [new_x,new_y]
        if (new_x == 5 and new_y>7) or (new_x == 6 and new_y>6) or (new_x == 7 and new_y>5) or (new_x == 8 and new_y>4):
            return False,[new_x,new_y]
        return True, [new_x,new_y]

offsetX = 260
offsetY = 40
middle = [[[offsetX, offsetY], [4, 0]],
          [[offsetX-45, offsetY+26], [3, 0]],
          [[offsetX+45, offsetY+26], [5, 0]],
          [[offsetX-90, offsetY+52], [2, 0]],
          [[offsetX, offsetY+52], [4, 1]],
          [[offsetX+90, offsetY+52], [6, 0]],
          [[offsetX-135, offsetY+78], [1, 0]],
          [[offsetX-45, offsetY+78], [3, 1]],
          [[offsetX+45, offsetY+78], [5, 1]],
          [[offsetX+135, offsetY+78], [7, 0]],
          [[offsetX-180, offsetY+104], [0, 0]],
          [[offsetX-90, offsetY+104], [2, 1]],
          [[offsetX, offsetY+104], [4, 2]],
          [[offsetX+90, offsetY+104], [6, 1]],
          [[offsetX+180, offsetY+104], [8, 0]],
          [[offsetX-135, offsetY+130], [1, 1]],
          [[offsetX-45, offsetY+130], [3, 2]],
          [[offsetX+45, offsetY+130], [5, 2]],
          [[offsetX+135, offsetY+130], [7, 1]],
          [[offsetX-180, offsetY+156], [0, 1]],
          [[offsetX-90, offsetY+156], [2, 2]],
          [[offsetX, offsetY+156], [4, 3]],
          [[offsetX+90, offsetY+156], [6, 2]],
          [[offsetX+180,offsetY+156], [8, 1]],
          [[offsetX-135, offsetY+182], [1, 2]],
          [[offsetX-45, offsetY+182], [3, 3]],
          [[offsetX+45, offsetY+182], [5, 3]],
          [[offsetX+135, offsetY+182], [7, 2]],
          [[offsetX-180, offsetY+208], [0, 2]],
          [[offsetX-90, offsetY+208], [2, 3]],
          [[offsetX, offsetY+208], [4, 4]],
          [[offsetX+90, offsetY+208], [6, 3]],
          [[offsetX+180, offsetY+208], [8, 2]],
          [[offsetX-135, offsetY+234], [1, 3]],
          [[offsetX-45, offsetY+234], [3, 4]],
          [[offsetX+45, offsetY+234], [5, 4]],
          [[offsetX+135, offsetY+234], [7, 3]],
          [[offsetX-180, offsetY+260], [0, 3]],
          [[offsetX-90, offsetY+260], [2, 4]],
          [[offsetX, offsetY+260], [4, 5]],
          [[offsetX+90, offsetY+260], [6, 4]],
          [[offsetX+180, offsetY+260], [8, 3]],
          [[offsetX-135, offsetY+286], [1, 4]],
          [[offsetX-45, offsetY+286], [3, 5]],
          [[offsetX+45, offsetY+286], [5, 5]],
          [[offsetX+135, offsetY+286], [7, 4]],
          [[offsetX-180, offsetY+312], [0, 4]],
          [[offsetX-90, offsetY+312], [2, 5]],
          [[offsetX, offsetY+312], [4, 6]],
          [[offsetX+90, offsetY+312], [6, 5]],
          [[offsetX+180, offsetY+312], [8, 4]],
          [[offsetX-135, offsetY+338], [1, 5]],
          [[offsetX-45, offsetY+338], [3, 6]],
          [[offsetX+45, offsetY+338], [5, 6]],
          [[offsetX+135, offsetY+338], [7, 5]],
          [[offsetX-90, offsetY+364], [2, 6]],
          [[offsetX, offsetY+364], [4, 7]],
          [[offsetX+90, offsetY+364], [6, 6]],
          [[offsetX-45, offsetY+390], [3, 7]],
          [[offsetX+45, offsetY+390], [5, 7]],
          [[offsetX, offsetY+416], [4, 8]]
          ]


def hex_corner(center, size, i):
    angle_deg = 60 * i
    angle_rad = math.pi / 180 * angle_deg
    return QPoint(center[0] + size * math.cos(angle_rad),
                 center[1] + size * math.sin(angle_rad))


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
                points = [hex_corner(element[0],size,0),
                    hex_corner(element[0],size,1),
                    hex_corner(element[0],size,2),
                    hex_corner(element[0], size, 3),
                    hex_corner(element[0], size, 4),
                    hex_corner(element[0], size, 5)]
                poly = QPolygon(points)
                painter.drawPolygon(poly)
                if txt != "":
                    painter.setPen(QPen(Qt.black, 10, Qt.SolidLine))
                    painter.drawText(QRectF(element[0][0]-30, element[0][1]-10,60,20),Qt.AlignHCenter|Qt.AlignVCenter, txt)

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.game = None
        self.buttons = []
        self.setButton("Dołącz!",self.start, offsetX-140, offsetY+600)
        self.setButton("Wyjdz!", self.quiteApp, offsetX+60, offsetY+600)
        self.scene = QGraphicsScene()
        self.view = None
        self.processing = False
        self.broken = False
        self.replaying = False
        self.InitWindow()
        self.timer = QElapsedTimer()
        self.history = None
        self.seconds = 0
        self.count = 0
        self.iterator = 0
        self.replay_window = None

    def my_replay(self):
        self.history = self.game.get_replay()
        self.replay_window = Replay()

    def replay(self):
        self.history = self.load_replay()
        self.replay_window = Replay()

    def InitWindow(self):
        self.setWindowTitle("2048 coronedition by Filip Flis - CLIENT")
        self.view = QGraphicsView(self.scene,self)
        self.view.setGeometry(0,0,560,600)
        self.setGeometry(900, 300, 560, 700)
        self.setMinimumWidth(560)
        self.setMinimumHeight(700)
        self.view.update()
        self.view.show()
        self.show()

    def update_scene(self):
        text = ""
        if self.broken:
            text ="Przeciwnik rozłączył się"
        elif self.processing:
            text = "Ruch przeciwnika"
        else:
            text = "Twój ruch"
        if self.game is not None:
            self.scene.clear()
            message = QGraphicsTextItem()
            message.setPlainText(text)
            self.scene.addItem(message)
            size = 30
            for element in middle:
                block = self.game.get_block(element[1][0],element[1][1])
                points = [hex_corner(element[0], size, 0),
                          hex_corner(element[0], size, 1),
                          hex_corner(element[0], size, 2),
                          hex_corner(element[0], size, 3),
                          hex_corner(element[0], size, 4),
                          hex_corner(element[0], size, 5)]
                poly = QPolygonF(points)
                polyitem = QGraphicsPolygonItem(poly)
                txt = ""
                message = QGraphicsTextItem()
                if block is not None:
                    txt = block.value_to_string()
                    if block.get_player() == 1:
                        polyitem.setBrush(QBrush(Qt.red, Qt.SolidPattern))
                    else:
                        polyitem.setBrush(QBrush(Qt.green, Qt.SolidPattern))
                else:
                    polyitem.setBrush(QBrush(Qt.lightGray, Qt.SolidPattern))
                message.setParentItem(polyitem)
                message.setPlainText(txt)
                font = QFont()
                font.setBold(True)
                font.setWeight(75)
                font.setPixelSize(12)
                message.setFont(font)
                message.setPos(QPointF(element[0][0]-(len(txt)*6), element[0][1]-12))
                polyitem.setPen(QPen(Qt.black, 5, Qt.SolidLine))
                self.scene.addItem(polyitem)


    def setButton(self,msg,action,x,y):
        btn1 = QPushButton(msg, self)
        btn1.move(x,y)
        btn1.clicked.connect(action)
        self.buttons.append(btn1)

    def start(self):
        self.buttons[0].setDisabled(True)
        self.update()
        self.game = Game()
        self.broken = False
        self.update_scene()


    def lets_process(self):
        self.game.send_and_listen()
        self.processing = False
        return True

    def quiteApp(self):
        userInfo = QMessageBox.question(self, "RLY?", "Chcesz wyjść?", QMessageBox.Yes | QMessageBox.No)
        if userInfo == QMessageBox.Yes:
            if self.game is not None:
                self.game.send_exit()
            myApp.exit()
        elif userInfo==QMessageBox.No:
            pass

    def keyPressEvent(self, event):
        if not self.processing:
            pressed = event.key()
            flag = False
            flag2 = False
            flag3 = False
            if pressed == Qt.Key_P:
                if not self.replaying and self.game is not None:
                    flag2 = True
                    self.my_replay()
            elif pressed == Qt.Key_O:
                if self.game is not None:
                    self.game.dump_state()
            elif pressed == Qt.Key_L:
                flag2 = True
                self.replay()
            elif pressed == Qt.Key_Q:
                if self.game.move_qt(3):
                    flag = True
            elif pressed == Qt.Key_W:
                if self.game.move_qt(4):
                    flag = True
            elif pressed == Qt.Key_E:
                if self.game.move_qt(5):
                    flag = True
            elif pressed == Qt.Key_A:
                if self.game.move_qt(2):
                    flag = True
            elif pressed == Qt.Key_S:
                if self.game.move_qt(1):
                    flag = True
            elif pressed == Qt.Key_D:
                if self.game.move_qt(6):
                    flag = True
            else:
                self.update_scene()
                pass
            self.update_scene()
            if flag and not self.broken:
                self.processing = True
                self.update_scene()
                worker = Worker(self.lets_process)
                worker.signals.finished.connect(self.update_scene)
                self.threadpool.start(worker)
            if flag2 and not self.replaying:
                self.replaying = True
                worker = Worker(self.play_replay)
                self.threadpool.start(worker)


    def play_replay(self):
        self.seconds = len(self.history)*2000
        self.count = 0
        self.iterator = -1
        self.timer.restart()
        while self.timer.elapsed() < self.seconds:
            self.count = self.timer.elapsed()/2000
            if self.iterator<self.count:
                self.iterator += 1
                try:
                    self.replay_window.recreate(self.history[self.iterator])
                except IndexError:
                    pass
                self.replay_window.update()
        self.replaying = False
        return True

    def load_replay(self):
        file = open("history.xml", "r")
        readed = file.read()
        file.close()
        readed = xmlrpc.client.loads(readed)
        tab = list(readed)
        proba = list(tab[0])
        return proba




if __name__ == '__main__':
    myApp = QApplication(sys.argv)
    window = Window()
    sys.exit(myApp.exec_())
