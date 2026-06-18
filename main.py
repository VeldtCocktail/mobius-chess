FILES = [chr(i) for i in range(ord("1"), ord("4") + 1)]
ROWS = [chr(i) for i in range(ord("a"), ord("h") + 1)]


class Square:
    def __init__(self, row, file):
        self.row = row
        self.file = file

    def __repr__(self):
        return f"Square({self.row}, {self.file})"


class Board:
    def __init__(self):
        self.board = [[Square(row, file) for file in FILES] for row in ROWS]

    def __repr__(self):
        return str(self.board)


board = Board()
print(board)
