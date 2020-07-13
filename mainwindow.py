import xmlrpc
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QLabel, QGraphicsScene, QGraphicsView, \
    QMainWindow, QGraphicsPolygonItem, QGraphicsTextItem, QLineEdit
from PySide2 import QtGui
from PySide2.QtGui import QPainter, QBrush, QPen, QPolygonF, QPolygon, QFont, QPixmap
from PySide2.QtCore import QPoint, Qt, QRectF, QPointF, QThreadPool, QRunnable, Slot, QObject, Signal, QElapsedTimer
import random
import math
import sys
import os
import socket
import traceback
from replaywindow import Replay, ReplayGame
from middles import middle, offsetY, offsetX
from cBlock import Block
from cBoard import Board
from cWorker import Worker
from cField import Field
from server import Networking_server
import clientgame
import hotseatgame
import servergame

# aby połączyć serwer z klientem należy najpierw w oknie serwera kliknąć "Nowa gra", a następnie w oknie klienta "Dołącz"
# po wykonaniu w oknie serwera pierwszego ruchu w oknie klienta pojawi się plansza
# pod przyciskiem O jest Zapisanie historii rozgrywki do pliku XML
# pod przyciskiem P jest odtworzenie replay'a aktualnej rozgrywki
# pod przyciskiem L jest odtworzenie replay'a rozgrywki z pliku xml






class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.game = None
        self.startbutton = self.setButton("Nowa Gra!",self.start, offsetX-140, offsetY+600)
        self.exitbutton = self.setButton("Wyjdz!", self.quiteApp, offsetX+60, offsetY+600)
        self.startserverbutton = self.setButton("Host game", self.startserver, offsetX-140, offsetY+640, False)
        self.startclientbutton = self.setButton("Join game", self.startclient, offsetX - 140, offsetY + 680, False)
        self.starthotseatbutton = self.setButton("Start hotseat \n game", self.starthotseat, offsetX - 140, offsetY + 720, False)
        self.textbox = QLineEdit(self)
        self.textbox.move(offsetX-30 , offsetY + 685)
        self.textbox.resize(100, 20)
        self.textbox.setVisible(False)
        self.show()
        self.gametype = None
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
        self.setGeometry(300, 300, 560, 800)
        self.setMinimumWidth(560)
        self.setMinimumHeight(800)
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
            text = "Opponent disconected"
        elif self.processing:
            text = "Opponent's turn"
        else:
            text = "Your turn"
        if self.gametype == "hotseat":
            if self.game.getplayer() == 1:
                text = "Player 1 moving"
            else:
                text = "Player 2 moving"
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


    def setButton(self,msg,action,x,y, visibility=True):
        btn1 = QPushButton(msg, self)
        btn1.move(x,y)
        btn1.clicked.connect(action)
        btn1.setVisible(visibility)
        return btn1


    def hidebuttons(self):
        self.startclientbutton.setVisible(False)
        self.startserverbutton.setVisible(False)
        self.starthotseatbutton.setVisible(False)
        self.textbox.setText("")
        self.textbox.setVisible(False)

    def showbuttons(self):
        self.startbutton.setVisible(False)
        self.startclientbutton.setVisible(True)
        self.startserverbutton.setVisible(True)
        self.starthotseatbutton.setVisible(True)
        self.textbox.setVisible(True)



    def startserver(self):
        self.broken = False
        self.game = servergame.Game()
        self.game.connect()
        self.gametype = "server"
        self.hidebuttons()
        self.update_scene()
        self.update()

    def start(self):
        self.showbuttons()

    def startclient(self):
        self.broken = False
        if self.checkip(self.textbox.text()):
            self.game = clientgame.Game()
            self.gametype = "client"
            self.hidebuttons()
            self.update_scene()
            self.update()
        else:
            userInfo = QMessageBox()
            userInfo.setWindowTitle("Error")
            userInfo.setText("Wrong IP address")
            userInfo.setStandardButtons(QMessageBox.Ok)
            userInfo.exec_()

    def starthotseat(self):
        self.broken = False
        self.game = hotseatgame.Game()
        self.gametype = "hotseat"
        self.hidebuttons()
        self.update_scene()
        self.update()

    def checkip(self, ip):
        if ip == "localhost":
            return True
        try:
            parts = ip.split('.')
            return len(parts) == 4 and all(0 <= int(part) < 256 for part in parts)
        except ValueError:
            return False
        except (AttributeError, TypeError):
            return False

    def lets_process(self):
        self.game.send_and_listen()
        self.processing = False
        return True

    def quiteApp(self):
        userInfo = QMessageBox.question(self, "Are You sure \n You want to quit?", QMessageBox.Yes | QMessageBox.No)
        if userInfo == QMessageBox.Yes:
            if self.game is not None:
                self.game.send_exit()
            self.threadpool = None
            myApp.exit()
        elif userInfo==QMessageBox.No:
            pass

    def keyPressEvent(self, event):
        if not self.processing:
            pressed = event.key()
            flag = False
            flag2 = False
            if pressed == Qt.Key_V:
                if not self.replaying and self.game is not None:
                    flag2 = True
                    self.my_replay()
            elif pressed == Qt.Key_B:
                if self.game is not None:
                    self.game.dump_state()
            elif pressed == Qt.Key_N:
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
            elif pressed == Qt.Key_U and self.gametype == "hotseat":
                self.game.moveQT(9)
            elif pressed == Qt.Key_I and self.gametype == "hotseat":
                self.game.moveQT(10)
            elif pressed == Qt.Key_O and self.gametype == "hotseat":
                self.game.moveQT(11)
            elif pressed == Qt.Key_J and self.gametype == "hotseat":
                self.game.moveQT(8)
            elif pressed == Qt.Key_K and self.gametype == "hotseat":
                self.game.moveQT(7)
            elif pressed == Qt.Key_L and self.gametype == "hotseat":
                self.game.moveQT(12)
            else:
                self.update_scene()
                pass
            self.update_scene()
            if flag and not self.broken and self.gametype == "server":
                self.processing = True
                self.update_scene()
                worker = Worker(self.lets_process)
                worker.signals.finished.connect(self.update_scene)
                self.threadpool.start(worker)
            if flag and not self.broken and self.gametype == "client":
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



if __name__ == '__main__':
    myApp = QApplication(sys.argv)
    window = Window()
    sys.exit(myApp.exec_())
