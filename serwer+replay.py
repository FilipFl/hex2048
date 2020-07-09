import xmlrpc
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QLabel, QGraphicsScene, QGraphicsView, QMainWindow, QGraphicsPolygonItem, QGraphicsTextItem
from PySide2 import QtGui
from PySide2.QtGui import QPainter, QBrush, QPen, QPolygonF, QPolygon, QFont, QPixmap
from PySide2.QtCore import QPoint, Qt, QRectF, QPointF, QThreadPool, QRunnable, Slot, QObject, Signal, QElapsedTimer
import random
import math
import sys
import os
import socket
import traceback
from klient import Replay, ReplayGame
from middles import middle, offsetY, offsetX
from cBlock import Block
from cBoard import Board
from cWorker import Worker
from cField import Field

# aby połączyć serwer z klientem należy najpierw w oknie serwera kliknąć "Nowa gra", a następnie w oknie klienta "Dołącz"
# po wykonaniu w oknie serwera pierwszego ruchu w oknie klienta pojawi się plansza
# pod przyciskiem O jest Zapisanie historii rozgrywki do pliku XML
# pod przyciskiem P jest odtworzenie replay'a aktualnej rozgrywki
# pod przyciskiem L jest odtworzenie replay'a rozgrywki z pliku xml



class Game:

    def __init__(self):
        self.playing_as = 1
        self.board = Board()
        self.board.create_block(1)
        self.done = False
        self.serwer = None
        self.replay = []
        self.replay.append(self.create_state())

    def connect(self):
        self.serwer = Networking_server()

    def send_exit(self):
        self.serwer.send("exit")

    def is_done(self):
        return self.done

    def finish_him(self):
        self.done = True


    def send_and_listen(self):
        state = self.create_state()
        self.replay.append(state)
        self.serwer.send(state)
        data = self.serwer.listening()
        if data:
            self.recreate_state(data)
            self.replay.append(state)


    def moveQT(self, click):
        if click == 1:
            if self.board.move_blocks(self.playing_as, 0):
                self.board.create_block(2)
                return True
        elif click == 2:
            if self.board.move_blocks(self.playing_as, 1):
                self.board.create_block(2)
                return True
        elif click == 3:
            if self.board.move_blocks(self.playing_as, 2):
                self.board.create_block(2)
                return True
        elif click == 4:
            if self.board.move_blocks(self.playing_as, 3):
                self.board.create_block(2)
                return True
        elif click == 5:
            if self.board.move_blocks(self.playing_as, 4):
                self.board.create_block(2)
                return True
        elif click == 6:
            if self.board.move_blocks(self.playing_as, 5):
                self.board.create_block(2)
                return True
        else:
            return False

    def create_state(self):
        game_state = []
        for element in middle:
            block = self.get_block(element[1][0],element[1][1])
            if block is not None:
                player = block.get_player()
                value = block.get_value()
            else:
                player = 0
                value = 0
            field = [element[1][0],element[1][1],player,value]
            game_state.append(field)
        return game_state

    def recreate_state(self, state):
        self.board = Board()
        self.board.recreate_map(state)

    def dump_state(self):
        test = xmlrpc.client.dumps(tuple(self.replay))
        file = open("history.xml", "w+")
        file.write(test)
        file.close()

    def load_replay(self):
        file = open("history.xml", "r")
        readed = file.read()
        file.close()
        readed = xmlrpc.client.loads(readed)
        tab = list(readed)
        proba = list(tab[0])
        return proba

    def get_replay(self):
        return self.replay

    def get_block(self,x,y):
        return self.board.get_field(x,y).get_block()



class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.game = None
        self.setButton("Nowa Gra!",self.start, offsetX-140, offsetY+600)
        self.setButton("Wyjdz!", self.quiteApp, offsetX+60, offsetY+600)
        self.scene = QGraphicsScene()
        self.view = None
        self.processing = False
        self.broken = False
        self.InitWindow()
        self.timer = QElapsedTimer()
        self.history = None
        self.seconds = 0
        self.count = 0
        self.iterator = 0
        self.replay_window = None
        self.replaying = False

    def hex_corner(self, center, size, i):
        angle_deg = 60 * i
        angle_rad = math.pi / 180 * angle_deg
        return QPoint(center[0] + size * math.cos(angle_rad),
                      center[1] + size * math.sin(angle_rad))

    def InitWindow(self):
        self.setWindowTitle("2048 coronedition by Filip Flis - SERWER")
        self.view = QGraphicsView(self.scene,self)
        self.view.setGeometry(0,0,560,600)
        self.setGeometry(300, 300, 560, 700)
        self.setMinimumWidth(560)
        self.setMinimumHeight(700)
        self.view.update()
        self.view.show()
        self.show()

    def my_replay(self):
        self.history = self.game.get_replay()
        self.replay_window = Replay()

    def replay(self):
        self.history = self.load_replay()
        self.replay_window = Replay()

    def update_scene(self):
        text = ""
        if self.broken:
            text = "Przeciwnik rozłączył się"
        elif self.processing:
            text = "Ruch przeciwnika"
        else:
            text = "Twój ruch"
        if self.game is not None:
            self.scene.clear()
            size = 30
            message = QGraphicsTextItem()
            message.setPlainText(text)
            self.scene.addItem(message)
            for element in middle:
                block = self.game.get_block(element[1][0],element[1][1])
                points = [self.hex_corner(element[0], size, 0),
                          self.hex_corner(element[0], size, 1),
                          self.hex_corner(element[0], size, 2),
                          self.hex_corner(element[0], size, 3),
                          self.hex_corner(element[0], size, 4),
                          self.hex_corner(element[0], size, 5)]
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
            self.view.update()
            self.view.show()


    def setButton(self,msg,action,x,y):
        btn1 = QPushButton(msg, self)
        btn1.move(x,y)
        btn1.clicked.connect(action)

    def start(self):
        self.broken = False
        self.game = Game()
        self.update_scene()
        self.game.connect()
        self.update_scene()
        self.update()



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
                if self.game.moveQT(3):
                    flag = True
            elif pressed == Qt.Key_W:
                if self.game.moveQT(4):
                    flag = True
            elif pressed == Qt.Key_E:
                if self.game.moveQT(5):
                    flag = True
            elif pressed == Qt.Key_A:
                if self.game.moveQT(2):
                    flag = True
            elif pressed == Qt.Key_S:
                if self.game.moveQT(1):
                    flag = True
            elif pressed == Qt.Key_D:
                if self.game.moveQT(6):
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
            if self.iterator < self.count:
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


class Networking_server:
    def __init__(self):
        self.connection = None
        self.client_address = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('', 10000)
        self.sock.bind(self.server_address)
        self.sock.listen()
        self.flag = False
        while not self.flag:
            self.connection, self.client_address = self.sock.accept()
            if self.connection:
                self.flag = True

    def send(self, message):
        message = str(message)
        message = message.encode()
        self.connection.sendall(message)

    def listening(self):
        txt = ""
        while txt != 'exit':
            try:
                data = self.connection.recv(4096)
                data = data.decode('utf-8')
                txt = data
                if txt == "exit":
                    self.broken = True
                data = eval(data)
                return data
            except:
                pass

    def close_it(self):
        self.sock.close()

if __name__ == '__main__':
    myApp = QApplication(sys.argv)
    window = Window()
    sys.exit(myApp.exec_())
