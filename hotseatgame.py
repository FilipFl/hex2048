from cBoard import Board
from middles import middle
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

    def get_player(self):
        return self.player_playing

    def is_done(self):
        return self.done

    def finish_him(self):
        self.done = True

    def change_player(self):
        if self.player_playing == 1:
            self.player_playing = 2
        else:
            self.player_playing = 1

    def move_qt(self, click):
        if self.player_playing == 1 and click <= 6:
            if self.board.move_blocks(self.player_playing, click):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.replay.append(self.create_state())
                self.check_all()
                return True
        elif self.player_playing == 2 and click > 6:
            if self.board.move_blocks(self.player_playing, click-6):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.replay.append(self.create_state())
                self.check_all()
                return True
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

    def check_all(self):
        thisturn = self.check_turn()
        self.last = thisturn
        if thisturn is False:
            self.change_player()
            self.board.create_block(self.player_playing)
            nextturn = self.check_turn()
            if nextturn is False:
                self.done = True
                userInfo = QMessageBox()
                userInfo.setWindowTitle("FINISH!")
                userInfo.setText("GAME ENDED!")
                userInfo.setStandardButtons(QMessageBox.Ok)
                userInfo.exec_()

    def get_block(self,x,y):
        return self.board.get_field(x,y).get_block()

    def check_turn(self):
        remstate = self.create_state()
        flag = False
        for i in range(6):
            if self.board.move_blocks(self.player_playing, i):
                flag = True
                self.recreate_state(remstate)
        return flag

    def get_score(self):
        return self.board.check_score()

    def get_replay(self):
        return self.replay
