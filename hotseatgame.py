from cBoard import Board
from middles import middle, offsetY, offsetX
from PySide2.QtWidgets import QMessageBox

class Game:

    def __init__(self):
        self.player_playing = 1
        self.board = Board()
        self.board.create_block(self.player_playing)
        self.done = False
        self.replay = []
        self.replay.append(self.create_state())
        self.last = None

    def getplayer(self):
        return self.player_playing

    def is_done(self):
        return self.done

    def finish_him(self):
        self.done = True

    def change_player(self):
        if self.player_playing ==1:
            self.player_playing = 2
        else:
            self.player_playing = 1

    def moveQT(self, click):
        if click == 1 and self.player_playing == 1:
            if self.board.move_blocks(self.player_playing, 0):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.checkall()
                return True
        elif click == 2 and self.player_playing == 1:
            if self.board.move_blocks(self.player_playing, 1):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.checkall()
                return True
        elif click == 3 and self.player_playing == 1:
            if self.board.move_blocks(self.player_playing, 2):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.checkall()
                return True
        elif click == 4 and self.player_playing == 1:
            if self.board.move_blocks(self.player_playing, 3):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.checkall()
                return True
        elif click == 5 and self.player_playing == 1:
            if self.board.move_blocks(self.player_playing, 4):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.checkall()
                return True
        elif click == 6 and self.player_playing == 1:
            if self.board.move_blocks(self.player_playing, 5):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.checkall()
                return True
        elif click == 7 and self.player_playing == 2:
            if self.board.move_blocks(self.player_playing, 0):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.checkall()
                return True
        elif click == 8 and self.player_playing == 2:
            if self.board.move_blocks(self.player_playing, 1):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.checkall()
                return True
        elif click == 9 and self.player_playing == 2:
            if self.board.move_blocks(self.player_playing, 2):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.checkall()
                return True
        elif click == 10 and self.player_playing == 2:
            if self.board.move_blocks(self.player_playing, 3):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.checkall()
                return True
        elif click == 11 and self.player_playing == 2:
            if self.board.move_blocks(self.player_playing, 4):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.checkall()
                return True
        elif click == 12 and self.player_playing == 2:
            if self.board.move_blocks(self.player_playing, 5):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.checkall()
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

    def checkall(self):
        thisturn = self.checkturn()
        self.last = thisturn
        if thisturn is False:
            self.change_player()
            nextturn = self.checkturn()
            if nextturn is False:
                self.done = True
                userInfo = QMessageBox()
                userInfo.setWindowTitle("FINISH!")
                userInfo.setText("GAME ENDED!")
                userInfo.setStandardButtons(QMessageBox.Ok)
                userInfo.exec_()

    def main_game(self):
        self.board.create_block(self.player_playing)
        self.change_player()

    def get_block(self,x,y):
        return self.board.get_field(x,y).get_block()

    def checkturn(self):
        remstate = self.create_state()
        flag = False
        for i in range (6):
            if self.board.move_blocks(self.player_playing, i):
                flag = True
                self.recreate_state(remstate)
        return flag


