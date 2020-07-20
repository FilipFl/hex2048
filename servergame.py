from cBoard import Board
from server import Networking_server
from middles import middle
from PySide2.QtWidgets import QMessageBox


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
            if data == "endgame":
                userInfo = QMessageBox()
                userInfo.setWindowTitle("FINISH!")
                userInfo.setText("GAME ENDED!")
                userInfo.setStandardButtons(QMessageBox.Ok)
                userInfo.exec_()
            else:
                self.recreate_state(data)
                self.replay.append(state)
                checkresult = self.check_both()
                if checkresult is False:
                    self.board.create_block(2)
                    state = self.create_state()
                    self.replay.append(state)
                    self.serwer.send(state)
                elif checkresult == "endgame":
                    self.serwer.send("endgame")

    def move_qt(self, click):
        if click == 1:
            if self.board.move_blocks(self.playing_as, 0):
                self.board.create_block(2)
                self.replay.append(self.create_state())
                return True
        elif click == 2:
            if self.board.move_blocks(self.playing_as, 1):
                self.board.create_block(2)
                self.replay.append(self.create_state())
                return True
        elif click == 3:
            if self.board.move_blocks(self.playing_as, 2):
                self.board.create_block(2)
                self.replay.append(self.create_state())
                return True
        elif click == 4:
            if self.board.move_blocks(self.playing_as, 3):
                self.board.create_block(2)
                self.replay.append(self.create_state())
                return True
        elif click == 5:
            if self.board.move_blocks(self.playing_as, 4):
                self.board.create_block(2)
                self.replay.append(self.create_state())
                return True
        elif click == 6:
            if self.board.move_blocks(self.playing_as, 5):
                self.board.create_block(2)
                self.replay.append(self.create_state())
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

    def get_replay(self):
        return self.replay

    def get_block(self,x,y):
        return self.board.get_field(x,y).get_block()

    def check_turn(self):
        remstate = self.create_state()
        flag = False
        for i in range(6):
            if self.board.move_blocks(self.playing_as, i):
                flag = True
                self.recreate_state(remstate)
        return flag

    def check_enemy_turn(self):
        enemy = 1
        if self.playing_as == 1:
            enemy = 2
        remstate = self.create_state()
        flag = False
        for i in range (6):
            if self.board.move_blocks(enemy, i):
                flag = True
                self.recreate_state(remstate)
        return flag

    def check_both(self):
        thisturn = self.check_turn()
        if not thisturn:
            nextturn = self.check_enemy_turn()
            if not nextturn:
                userInfo = QMessageBox()
                userInfo.setWindowTitle("FINISH!")
                userInfo.setText("GAME ENDED!")
                userInfo.setStandardButtons(QMessageBox.Ok)
                userInfo.exec_()
                return "endgame"
        return thisturn

    def get_score(self):
        return self.board.check_score()
