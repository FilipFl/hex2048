from cBoard import Board
from middles import middle
from PySide2.QtWidgets import QMessageBox
import random


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
        if click == 1 and self.player_playing == 1:
            if self.board.move_blocks(self.player_playing, 0):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.replay.append(self.create_state())
                self.check_all()
                return True
        elif click == 2 and self.player_playing == 1:
            if self.board.move_blocks(self.player_playing, 1):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.replay.append(self.create_state())
                self.check_all()
                return True
        elif click == 3 and self.player_playing == 1:
            if self.board.move_blocks(self.player_playing, 2):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.replay.append(self.create_state())
                self.check_all()
                return True
        elif click == 4 and self.player_playing == 1:
            if self.board.move_blocks(self.player_playing, 3):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.replay.append(self.create_state())
                self.check_all()
                return True
        elif click == 5 and self.player_playing == 1:
            if self.board.move_blocks(self.player_playing, 4):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.replay.append(self.create_state())
                self.check_all()
                return True
        elif click == 6 and self.player_playing == 1:
            if self.board.move_blocks(self.player_playing, 5):
                self.change_player()
                self.board.create_block(self.player_playing)
                self.replay.append(self.create_state())
                self.check_all()
                return True
        else:
            return False

    def move_ai(self):
        direction = self.predict_and_find()
        self.board.move_blocks(self.player_playing, direction)
        self.change_player()
        self.board.create_block(self.player_playing)
        self.replay.append(self.create_state())
        self.check_all()

    def predict_and_find(self):
        curr_state = self.create_state()
        curr_player = self.player_playing
        steps = []
        best_enemy_steps = []
        my_evaluation = []
        for i in range(6):
            self.recreate_state(curr_state)
            self.board.move_blocks(self.player_playing, i)
            if self.check_player_turn(1):
                steps.append([True, self.create_state(), i])
            else:
                return i
        for i in range(6):
            self.player_playing = 1
            evaluation = []
            for j in range(6):
                self.recreate_state(steps[i][1])
                self.board.move_blocks(self.player_playing, j)
                evaluation.append([self.evaluate_enemy(), i, j])
            best = evaluation.index(max(evaluation))
            self.recreate_state(steps[i][1])
            self.board.move_blocks(self.player_playing, evaluation[best][2])
            best_enemy_steps.append([self.create_state(), i, evaluation[best][2]])
        for i in range(6):
            self.player_playing = 2
            for j in range(6):
                self.recreate_state(best_enemy_steps[i][0])
                self.board.move_blocks(self.player_playing, j)
                if not self.check_player_turn(1):
                    my_evaluation.append([self.evaluate_me()*2, i, j])
                else:
                    my_evaluation.append([self.evaluate_me(), i, j])
        random.shuffle(my_evaluation)
        my_best = my_evaluation.index(max(my_evaluation))
        while not self.board.move_blocks(self.player_playing, best_enemy_steps[my_evaluation[my_best][1]][1]):
            my_evaluation.pop(my_best)
            random.shuffle(my_evaluation)
            my_best = my_evaluation.index(max(my_evaluation))
        self.recreate_state(curr_state)
        self.player_playing = curr_player
        return best_enemy_steps[my_evaluation[my_best][1]][1]

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

    def check_player_turn(self, player):
        remstate = self.create_state()
        flag = False
        for i in range(6):
            if self.board.move_blocks(player, i):
                flag = True
                self.recreate_state(remstate)
        return flag

    def get_score(self):
        return self.board.check_score()

    def get_replay(self):
        return self.replay

    def evaluate_enemy(self):
        score = self.board.check_score()
        return (score[0][0]+(score[0][0]-score[1][0]))*score[1][1]/score[0][1]

    def evaluate_me(self):
        score = self.board.check_score()
        return (score[1][0]+(score[1][0]-score[0][0]))*score[0][1]/score[1][1]
