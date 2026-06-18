COLUMNS = [chr(i) for i in range(ord("a"), ord("d") + 1)]
ROWS = [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
]


class Square:
    """Represents a square on the board."""

    def __init__(self, row, column):
        """
        Initializes a square with the given row and col.
        Parameters:
            row (str): The row of the square.
            column (str): The column of the square.
        """
        self.row = row
        self.column = column

    def __repr__(self):
        """
        Returns a string representation of the square.
        """
        return f"Square({self.column}, {self.row})"


class Board:
    """
    Represents the mobius chess board.
    Row number 1 are the first raw for white pieces
    """

    def __init__(self):
        """
        Initializes the board with a 2D list of squares.
        """
        self.board = [[Square(row, column) for column in COLUMNS] for row in ROWS]

    def __repr__(self):
        """
        Returns a string representation of the board.
        """
        return str(self.board)

    def get_square(self, row, column):
        """
        Returns the square at the given row and column.
        Parameters:
            row (int): The row of the square.
            column (str): The column of the square.
        """
        return self.board[row][ord(column) - ord("a")]


class Piece:
    """Represents a piece on the board."""

    def __init__(self, type, color):
        """
        Initializes a piece with the given type and color.
        Parameters:
            type (str): The type of the piece (ex: "P", "R", etc.).
            color (str): The color of the piece (ex: "w", "b").
        """
        self.type = type
        self.color = color
        self.has_moved = False  # For en-passant handling. Will be common to all
        # pieces anyway.
        self.piece_list = [
            Piece("K", "w"),  # Kings
            Piece("K", "b"),
            Piece("Q", "w"),  # Queens
            Piece("Q", "b"),
            Piece("R", "w"),  # Rooks
            Piece("R", "b"),
            Piece("B", "w"),  # Bishops
            Piece("B", "b"),
            Piece("N", "w"),  # Knights
            Piece("N", "b"),
            Piece("P", "w"),  # Pawns
            Piece("P", "b"),
        ]

    def __repr__(self):
        """
        Returns a string representation of the piece.
        """
        return f"Piece({self.type}, {self.color})"


board = Board()
print(board)
