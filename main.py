COLUMNS = [chr(i) for i in range(ord("a"), ord("d") + 1)]
ROWS = [i for i in range(1, 17)]

WHITE_QUEEN_ROW = 1
WHITE_KING_ROW = 16
BLACK_QUEEN_ROW = 8
BLACK_KING_ROW = 9
WHITE_PAWNS_ROWS = [2, 15]
BLACK_PAWNS_ROWS = [7, 10]
COLUMN_ROOKS = "a"
COLUMN_KNIGHTS = "b"
COLUMN_BISHOPS = "c"


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
        self.piece = None

    def get_piece(self):
        return self.piece

    def set_piece(self, pce):
        self.piece = pce

    def __repr__(self):
        """
        Returns a string representation of the square.
        """
        return f"Square({self.column}, {self.row}, {self.piece})"


class Board:
    """
    Represents the mobius chess board.
    Rows number 1, 2, 15 and 16 are the white pieces starting rows.
    The white queen starts on D1 and the white king starts on D16.
    """

    def __init__(self):
        """
        Initializes the board with a 2D list of squares.
        """
        self.board = [[Square(row, column) for column in COLUMNS] for row in ROWS]

    def set_piece(self, col, row, piece):
        self.board[row - 1][COLUMNS.index(col)].set_piece(piece)

    def get_piece(self, col, row):
        return self.board[row - 1][COLUMNS.index(col)].get_piece()

    def __repr__(self):
        """
        Returns a string representation of the board.
        """
        return str(self.board)


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
        # pieces anyway

    def __repr__(self):
        """
        Returns a string representation of the piece.
        """
        return f"Piece({self.type}, {self.color})"


class Game:
    """Represents the game of mobius chess."""

    def fill_pieces(self, board):
        """
        Fills the board with pieces in their starting positions.
        Parameters:
            board (Board): The board to fill with pieces.
        """
        # White Pieces
        # Rooks
        board.set_piece(COLUMN_ROOKS, 16, Piece("R", "w"))
        board.set_piece(COLUMN_ROOKS, 1, Piece("R", "w"))
        # Knights
        board.set_piece(COLUMN_KNIGHTS, 16, Piece("N", "w"))
        board.set_piece(COLUMN_KNIGHTS, 1, Piece("N", "w"))
        # Bishops
        board.set_piece(COLUMN_KNIGHTS, 16, Piece("B", "w"))
        board.set_piece(COLUMN_BISHOPS, 1, Piece("B", "w"))
        # Queen
        board.set_piece("d", WHITE_QUEEN_ROW, Piece("Q", "w"))
        # King
        board.set_piece("d", WHITE_KING_ROW, Piece("K", "w"))

        # Black Pieces
        # Rooks
        board.set_piece(COLUMN_ROOKS, 9, Piece("R", "b"))
        board.set_piece(COLUMN_ROOKS, 8, Piece("R", "b"))
        # Knights
        board.set_piece(COLUMN_KNIGHTS, 9, Piece("N", "b"))
        board.set_piece(COLUMN_KNIGHTS, 8, Piece("N", "b"))
        # Bishops
        board.set_piece(COLUMN_KNIGHTS, 9, Piece("B", "b"))
        board.set_piece(COLUMN_BISHOPS, 8, Piece("B", "b"))
        # Queen
        board.set_piece("d", BLACK_QUEEN_ROW, Piece("Q", "b"))
        # King
        board.set_piece("d", BLACK_KING_ROW, Piece("K", "b"))

    def __init__(self):
        """
        Initializes the game with a board and a piece list.
        """
        self.board = Board()
        self.fill_pieces(self.board)


board = Board()
print(board)

board.set_piece("c", 2, Piece("P", "w"))
print(board.get_piece("c", 2))

game = Game()
print(game.board)
