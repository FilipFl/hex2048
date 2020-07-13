import random
from middles import middle, offsetX, offsetY
from cField import Field
from cBlock import Block

class Board:
    def __init__(self):
        self.map = []
        for i in range(0,9):
            row = []
            if i==0 or i==8:
                for j in range(0,5):
                    f = Field(i, j)
                    row.append(f)
            if i==1 or i==7:
                for j in range(0,6):
                    f = Field(i,j)
                    row.append(f)
            if i==2 or i==6:
                for j in range(0,7):
                    f = Field(i,j)
                    row.append(f)
            if i==3 or i==5:
                for j in range(0,8):
                    f = Field(i,j)
                    row.append(f)
            else:
                for j in range(0,9):
                    f= Field(i,j)
                    row.append(f)
            self.map.append(row)

    def get_field(self,x,y):
        return self.map[x][y]

    def recreate_map(self, state):
        for element in state:
            field = self.get_field(element[0],element[1])
            if element[2] != 0:
                field.make_block(element[2], element[3])
    # metoda co runde tworząca klocek aktualnie grającego gracza

    def create_block(self, player):
        count = 0
        for element in middle:
            x = element[1][0]
            y = element[1][1]
            possible = self.get_field(x, y).get_block()
            if possible is not None:
                count += 1
        if count != len(middle):
            done = False
            while not done:
                x = random.randint(0, 9)
                y = random.randint(0, 9)
                status, ble = self.check_bound(x,y)
                if status:
                    possible = self.get_field(x,y).get_block()
                    if possible is None:
                        self.get_field(x, y).make_block(player)
                        done = True

    def create_state(self):
        game_state = []
        for element in middle:
            block = self.get_field(element[1][0], element[1][1]).get_block()
            if block is not None:
                player = block.get_player()
                value = block.get_value()
            else:
                player = 0
                value = 0
            field = [element[1][0], element[1][1], player, value]
            game_state.append(field)
        return game_state

    def move_blocks(self,player, dir):
        blocks = []
        iterations = -1
        old_state = self.create_state()
        for column in self.map:
            for field in column:
                block = field.get_block()
                if block != None:
                    if block.get_player() == player:
                        blocks.append(block)
        # przesuwanie każdego klocka po kolei, aż nic się nie będzie zmieniać na planszy
        nothing_changed = False
        while not nothing_changed:
            # określenie które klocki powinny poruszać się najpierw, w zależności jaki kierunek ruchu
            if dir == 0:
                blocks.sort(key=lambda x: x.get_y(), reverse=True)
            if dir == 3:
                blocks.sort(key=lambda x: x.get_y())
            if dir == 2:
                blocks.sort(key=lambda x: x.get_x())
            if dir == 5:
                blocks.sort(key=lambda x: x.get_x(), reverse=True)
            if dir == 1:
                blocks.sort(key=lambda x: x.get_x())
            if dir == 4:
                blocks.sort(key=lambda x: x.get_x(), reverse=True)
            nothing_changed = True
            for item in blocks:
                iterations += 1
                old = item.get_coords()
                possible, new_coords = item.get_adress_to_move(dir)
                if possible:
                    existing = self.get_field(new_coords[0], new_coords[1]).get_block()
                    if existing is not None:
                        if existing.get_player() == player and existing.get_value() == item.get_value():
                            existing.mul_value()
                            blocks.remove(item)
                            self.get_field(old[0], old[1]).del_block()
                            nothing_changed = False
                    else:
                        item.set_coords(new_coords)
                        self.get_field(new_coords[0],new_coords[1]).asign_block(item)
                        self.get_field(old[0], old[1]).del_block()
                        nothing_changed = False
        #sprawdzenie czy cokolwiek się zmieniło jeśli nie, ruch niepoprawny
        new_state = self.create_state()
        if old_state == new_state:
            return False
        else:
            return True

    # sprawdzenie czy współrzędne znajdują się na mapie
    def check_bound(self, x, y):
        if x < 0 or y < 0 or x > 8:
            return False, [x, y]
        if x < 5:
            if y - x > 4:
                return False, [x, y]
        if (x == 5 and y > 7) or (x == 6 and y > 6) or (x == 7 and y > 5) or (x == 8 and y > 4):
            return False, [x, y]
        return True, [x, y]

