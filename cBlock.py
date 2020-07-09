class Block:
    def __init__(self, player, x, y, value):
        self.value = value
        self.owned_by = player
        self.x_pos = x
        self.y_pos = y

    def mul_value(self):
        self.value = self.value * 2

    def get_value(self):
        return self.value

    def get_player(self):
        return self.owned_by

    def get_coords(self):
        return [self.x_pos, self.y_pos]

    def set_coords(self, lista):
        self.x_pos = lista[0]
        self.y_pos = lista[1]

    def get_x(self):
        return self.x_pos

    def get_y(self):
        return self.y_pos

    def value_to_string(self):
        # funkcja do printowania wartości
        s = ''
        s += str(self.value)
        return s


def get_adress_to_move(self, dir):
    # 0 - w dół
    # 1 - lewo dół
    # 2 - lewo góra
    # 3 - góra
    # 4 - prawo góra
    # 5 - prawo dół
    directions = []
    if self.x_pos < 4:
        directions = [[0, +1], [-1, 0], [-1, -1], [0, -1], [+1, 0], [+1, +1]]
    elif self.x_pos > 4:
        directions = [[0, +1], [-1, +1], [-1, 0], [0, -1], [+1, -1], [+1, 0]]
    else:
        directions = [[0, +1], [-1, 0], [-1, -1], [0, -1], [+1, -1], [+1, 0]]
    get_dir = directions[dir]
    new_x = get_dir[0] + self.x_pos
    new_y = get_dir[1] + self.y_pos
    if new_x < 0 or new_y < 0 or new_x > 8:
        return False, [new_x, new_y]
    if new_x < 5:
        if new_y - new_x > 4:
            return False, [new_x, new_y]
    if (new_x == 5 and new_y > 7) or (new_x == 6 and new_y > 6) or (new_x == 7 and new_y > 5) or (
            new_x == 8 and new_y > 4):
        return False, [new_x, new_y]
    return True, [new_x, new_y]




