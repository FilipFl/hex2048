from client import Networking_client
from cBoard import Board
import xmlrpc

class Game:

    def __init__(self):
        self.playing_as = 2
        self.board = Board()
        self.done = False
        self.client = Networking_client()
        data = self.client.listening()
        self.recreate_state(data)
        self.replay = []
        self.replay.append(data)
        self.memorized_state = None

    def prep_for_replay(self):
        self.memorized_state = self.create_state()

    def after_rep(self):
        self.recreate_state(self.memorized_state)

    def send_exit(self):
        self.client.send("exit")

    def is_done(self):
        return self.done

    def finish_him(self):
        self.done = True

    def send_and_listen(self):
        state = self.create_state()
        self.replay.append(state)
        self.client.send(state)
        data = self.client.listening()
        if data:
            self.recreate_state(data)
            self.replay.append(data)


    def moveQT(self, click):
        if click == 1:
            if self.board.move_blocks(self.playing_as, 0):
                self.board.create_block(1)
                return True
        elif click == 2:
            if self.board.move_blocks(self.playing_as, 1):
                self.board.create_block(1)
                return True
        elif click == 3:
            if self.board.move_blocks(self.playing_as, 2):
                self.board.create_block(1)
                return True
        elif click == 4:
            if self.board.move_blocks(self.playing_as, 3):
                self.board.create_block(1)
                return True
        elif click == 5:
            if self.board.move_blocks(self.playing_as, 4):
                self.board.create_block(1)
                return True
        elif click == 6:
            if self.board.move_blocks(self.playing_as, 5):
                self.board.create_block(1)
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
        file = open("history.xml","w+")
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


    def main_game(self):
        self.board.create_block(self.player_playing)
        self.move()
        self.change_player()

    def get_block(self,x,y):
        return self.board.get_field(x,y).get_block()