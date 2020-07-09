from cBlock import Block

class Field:
    def __init__(self, x, y):
        self.pos_x = x
        self.pos_y = y
        self.blocked = None

    def make_block(self, player, value=2):
        self.blocked = Block(player, self.pos_x, self.pos_y, value)

    def del_block(self):
        self.blocked = None

    def asign_block(self,block):
        self.blocked = block

    def get_block(self):
        return self.blocked
