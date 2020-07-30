from PySide2.QtWidgets import QApplication, QPushButton, QMessageBox, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, \
    QMainWindow, QGraphicsPolygonItem, QGraphicsTextItem, QLineEdit
from PySide2.QtGui import QBrush, QPen, QPolygonF, QFont, QPixmap, QColor, QPainter
from PySide2.QtCore import QPoint, Qt, QPointF, QThreadPool, QElapsedTimer
import math
import sys
from replaywindow import Replay
from middles import middle, offsetY, offsetX
from cWorker import Worker
import clientgame
import hotseatgame
import servergame
import infowindow
import aigame
from PySide2.QtCore import *


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.game = None
        self.startbutton = self.set_button("New Game", self.start, offsetX - 140, offsetY + 600)
        self.exitbutton = self.set_button("Quit", self.quit_app, offsetX - 140, offsetY + 680)
        self.startserverbutton = self.set_button("Host game", self.start_server, offsetX, offsetY + 600, False)
        self.startclientbutton = self.set_button("Join game", self.start_client, offsetX, offsetY + 640, False)
        self.starthotseatbutton = self.set_button("Start hotseat \n game", self.start_hot_seat, offsetX, offsetY + 680, False)
        self.startaibutton = self.set_button("Start AI game", self.start_ai, offsetX, offsetY + 720, False)
        self.infobutton = self.set_button("Info", self.show_info, offsetX - 140, offsetY+640)
        self.textbox = QLineEdit(self)
        self.textbox.move(offsetX+110, offsetY + 645)
        self.textbox.resize(100, 20)
        self.textbox.setVisible(False)
        self.show()
        self.gametype = None
        self.scene = QGraphicsScene()
        self.view = None
        self.processing = False
        self.broken = False
        self.path_to_graphics = "graphics/"
        self.init_window(self.path_to_graphics)
        self.timer = QElapsedTimer()
        self.history = None
        self.seconds = 0
        self.count = 0
        self.iterator = 0
        self.replay_window = None
        self.replaying = False
        self.worker = None
        self.info = None
        self.timer = QElapsedTimer()



    def hex_corner(self, center, size, i):
        angle_deg = 60 * i
        angle_rad = math.pi / 180 * angle_deg
        return QPoint(center[0] + size * math.cos(angle_rad),
                      center[1] + size * math.sin(angle_rad))

    def init_window(self,path):
        self.setWindowTitle("Hexagonal 2048 by FF")
        self.setGeometry(100, 100, offsetX*2, 800)
        self.scene.setSceneRect(0,0,offsetX*2,600)
        self.view = QGraphicsView(self.scene, self)
        self.view.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.view.setGeometry(0,0,offsetX*2,600)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMinimumWidth(offsetX*2)
        self.setMinimumHeight(800)
        self.setMaximumHeight(800)
        self.setMaximumWidth(offsetX*2)
        self.scene.setBackgroundBrush(QBrush(QPixmap(path+"background3top.jpg")))
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
        elif self.processing and self.gametype == "ai":
            text = "AI turn"
        elif self.processing:
            text = "Opponent's turn"
        else:
            text = "Your turn"
        if self.gametype == "hotseat":
            if self.game.get_player() == 1:
                text = "Player 1 moving"
            else:
                text = "Player 2 moving"
        if self.game is not None:
            self.scene.clear()
            self.scene.setBackgroundBrush(QBrush(QPixmap(self.path_to_graphics+"background3top.jpg")))
            size = 30
            message = QGraphicsTextItem()
            message.setPlainText(text)
            font = QFont()
            font.setBold(True)
            font.setWeight(75)
            font.setPixelSize(12)
            message.setFont(font)
            message.setDefaultTextColor(QColor(255, 255, 255))
            self.scene.addItem(message)
            score = self.game.get_score()
            text = "Player 1 score: {} \nPlayer 1 blocks: {}\n\nPlayer 2 score: {}\nPlayer 2 blocks: {}".format(
                score[0][0], score[0][1], score[1][0], score[1][1]
            )
            message = QGraphicsTextItem()
            message.setPlainText(text)
            message.setPos(QPointF(0, offsetY+400))
            message.setFont(font)
            message.setDefaultTextColor(QColor(255, 255, 255))
            self.scene.addItem(message)
            i = 0
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
                        polyitem.setBrush(QBrush(QColor(255,255,255), Qt.SolidPattern))
                    else:
                        polyitem.setBrush(QBrush(QColor(25,25,25), Qt.SolidPattern))
                        message.setDefaultTextColor(QColor(255,255,255))
                else:
                    polyitem.setBrush(QBrush(QColor(14,41,75), Qt.SolidPattern))
                message.setParentItem(polyitem)
                message.setPlainText(txt)
                font = QFont()
                font.setBold(True)
                font.setWeight(75)
                font.setPixelSize(12)
                message.setFont(font)
                message.setPos(QPointF(element[0][0]-(len(txt)*6), element[0][1]-12))
                polyitem.setPen(QPen(QColor(179,236,255), 5, Qt.SolidLine))
                self.startpoly = poly
                self.testpoly = polyitem
                self.scene.addItem(polyitem)
                if i == 1:
                    self.destpoly = poly
                i += 1
            self.view.update()
            self.view.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        background = QPixmap(self.path_to_graphics+"background3bot.jpg")
        painter.drawPixmap(QPoint(0,600), background)


    def set_button(self, msg, action, x, y, visibility=True):
        btn1 = QPushButton(msg, self)
        btn1.move(x,y)
        btn1.clicked.connect(action)
        btn1.setVisible(visibility)
        return btn1

    def hide_buttons(self):
        self.startclientbutton.setVisible(False)
        self.startserverbutton.setVisible(False)
        self.starthotseatbutton.setVisible(False)
        self.startaibutton.setVisible(False)
        self.textbox.setText("")
        self.textbox.setVisible(False)


    def show_buttons(self):
        self.startclientbutton.setVisible(True)
        self.startserverbutton.setVisible(True)
        self.starthotseatbutton.setVisible(True)
        self.startaibutton.setVisible(True)
        self.textbox.setVisible(True)

    def start_server(self):
        self.broken = False
        self.game = servergame.Game()
        self.game.connect()
        self.gametype = "server"
        self.hide_buttons()
        self.update_scene()
        self.update()

    def start(self):
        self.show_buttons()

    def start_client(self):
        self.broken = False
        if self.check_ip(self.textbox.text()):
            self.game = clientgame.Game(self.textbox.text())
            self.gametype = "client"
            self.hide_buttons()
            self.update_scene()
            self.update()
        else:
            userInfo = QMessageBox()
            userInfo.setWindowTitle("Error")
            userInfo.setText("Wrong IP address")
            userInfo.setStandardButtons(QMessageBox.Ok)
            userInfo.exec_()

    def start_hot_seat(self):
        self.broken = False
        self.game = hotseatgame.Game()
        self.gametype = "hotseat"
        self.hide_buttons()
        self.update_scene()
        self.update()

    def start_ai(self):
        self.game = aigame.Game()
        self.gametype = "ai"
        self.hide_buttons()
        self.update_scene()
        self.update()

    def show_info(self):
        self.info = infowindow.InfoWindow(self.path_to_graphics+"info.jpg")

    def check_ip(self, ip):
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

    def lets_wait(self):
        self.timer.start()
        while self.timer.elapsed() < 3000:
            pass
        self.processing = False
        return True

    def quit_app(self):
        userInfo = QMessageBox.question(self, "Quiting", "Do You want to quit?", (QMessageBox.Yes | QMessageBox.No))
        if userInfo == QMessageBox.Yes:
            if self.game is not None and self.gametype != "hotseat" and self.gametype != "ai":
                self.game.send_exit()
            self.threadpool.cancel(self.worker)
            myApp.exit()
        elif userInfo==QMessageBox.No:
            pass

    def keyPressEvent(self, event):
        pressed = event.key()
        if not self.processing:
            pressed = event.key()
            flag = False
            flag2 = False
            if pressed == Qt.Key_V:
                if not self.replaying and self.game is not None:
                    flag2 = True
                    self.my_replay()
            elif pressed == Qt.Key_N:
                flag2 = True
                self.replay()
            elif pressed == Qt.Key_Q:
                if self.game.move_qt(3):
                    self.processing = True
                    flag = True
            elif pressed == Qt.Key_W:
                if self.game.move_qt(4):
                    self.processing = True
                    flag = True
            elif pressed == Qt.Key_E:
                if self.game.move_qt(5):
                    self.processing = True
                    flag = True
            elif pressed == Qt.Key_A:
                if self.game.move_qt(2):
                    self.processing = True
                    flag = True
            elif pressed == Qt.Key_S:
                if self.game.move_qt(1):
                    self.processing = True
                    flag = True
            elif pressed == Qt.Key_D:
                if self.game.move_qt(6):
                    self.processing = True
                    flag = True
            elif pressed == Qt.Key_U and self.gametype == "hotseat":
                self.game.move_qt(9)
            elif pressed == Qt.Key_I and self.gametype == "hotseat":
                self.game.move_qt(10)
            elif pressed == Qt.Key_O and self.gametype == "hotseat":
                self.game.move_qt(11)
            elif pressed == Qt.Key_J and self.gametype == "hotseat":
                self.game.move_qt(8)
            elif pressed == Qt.Key_K and self.gametype == "hotseat":
                self.game.move_qt(7)
            elif pressed == Qt.Key_L and self.gametype == "hotseat":
                self.game.move_qt(12)
            else:
                self.update_scene()
                pass
            self.update_scene()
            if self.processing and self.gametype == "hotseat":
                self.processing = False
            if flag and not self.broken and self.gametype == "server":
                self.processing = True
                self.update_scene()
                worker = Worker(self.lets_process)
                self.worker = worker
                worker.signals.finished.connect(self.update_scene)
                self.threadpool.start(worker)
            if flag and not self.broken and self.gametype == "client":
                self.processing = True
                self.update_scene()
                worker = Worker(self.lets_process)
                self.worker = worker
                worker.signals.finished.connect(self.update_scene)
                self.threadpool.start(worker)
            if flag and self.gametype == "ai":
                self.update_scene()
                worker = Worker(self.lets_wait)
                self.worker = worker
                worker.signals.finished.connect(self.update_ai)
                self.threadpool.start(worker)
            if flag2 and not self.replaying:
                self.replaying = True
                worker = Worker(self.play_replay)
                self.threadpool.start(worker)

    def update_ai(self):
        self.game.move_ai()
        self.update_scene()

    def play_replay(self):
        self.seconds = len(self.history)*2000
        self.count = 0
        self.iterator = -1
        self.timer.restart()
        while self.timer.elapsed() < self.seconds:
            if not self.replay_window.isVisible():
                self.replaying = False
                break
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


if __name__ == '__main__':
    myApp = QApplication(sys.argv)
    window = Window()
    sys.exit(myApp.exec_())
