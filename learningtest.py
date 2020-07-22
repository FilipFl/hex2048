import numpy as np
from cBoard import Board
from middles import middle
import tensorflow as tf
import random
from tensorflow import keras

class Game:
    def __init__(self):
        self.player_playing = 1
        self.board = Board()
        self.board.create_block(self.player_playing)
        self.done = False
        self.last = None

    def get_player(self):
        return self.player_playing

    def change_player(self):
        if self.player_playing == 1:
            self.player_playing = 2
        else:
            self.player_playing = 1

    def move_randomly(self):
        direction = random.randint(0, 5)
        while not self.board.move_blocks(2, direction):
            direction = random.randint(0, 5)
        self.change_player()
        self.board.create_block(self.player_playing)
        self.check_all()

    def move_network(self, dir):
        self.board.move_blocks(1, dir)
        self.change_player()
        self.board.create_block(self.player_playing)
        self.check_all()
        self.move_randomly()

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
            field = [player, value]
            game_state.append(field)
        return np.array(game_state)

    def recreate_state(self, state):
        self.board = Board()
        self.board.recreate_map(state)

    def check_all(self):
        thisturn = self.check_turn()
        self.last = thisturn
        if thisturn is False:
            self.change_player()
            nextturn = self.check_turn()
            if nextturn is False:
                self.done = True
                self.board = Board()
                self.player_playing = 1
                self.board.create_block(self.player_playing)
                self.done = False

    def get_block(self, x, y):
        return self.board.get_field(x, y).get_block()

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

    def evaluation(self):
        score = self.board.check_score()
        return (score[0][0]+(score[0][0]-score[1][0]))*(score[1][1]/score[0][1])

