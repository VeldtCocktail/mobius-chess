COLUMNS = [chr(i) for i in range(ord("a"), ord("d") + 1)]
ROWS = [i for i in range(1, 17)]

NUM_ROWS = len(ROWS)
NUM_COLS = len(COLUMNS)

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

    def get_square(self, col, row) -> Square:
        return self.board[row - 1][COLUMNS.index(col)]

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
        board.set_piece(COLUMN_ROOKS, WHITE_KING_ROW, Piece("R", "w"))
        board.set_piece(COLUMN_ROOKS, WHITE_QUEEN_ROW, Piece("R", "w"))
        # Knights
        board.set_piece(COLUMN_KNIGHTS, WHITE_KING_ROW, Piece("N", "w"))
        board.set_piece(COLUMN_KNIGHTS, WHITE_QUEEN_ROW, Piece("N", "w"))
        # Bishops
        board.set_piece(COLUMN_BISHOPS, WHITE_KING_ROW, Piece("B", "w"))
        board.set_piece(COLUMN_BISHOPS, WHITE_QUEEN_ROW, Piece("B", "w"))
        # Queen
        board.set_piece("d", WHITE_QUEEN_ROW, Piece("Q", "w"))
        # King
        board.set_piece("d", WHITE_KING_ROW, Piece("K", "w"))

        # Black Pieces
        # Rooks
        board.set_piece(COLUMN_ROOKS, BLACK_KING_ROW, Piece("R", "b"))
        board.set_piece(COLUMN_ROOKS, BLACK_QUEEN_ROW, Piece("R", "b"))
        # Knights
        board.set_piece(COLUMN_KNIGHTS, BLACK_KING_ROW, Piece("N", "b"))
        board.set_piece(COLUMN_KNIGHTS, BLACK_QUEEN_ROW, Piece("N", "b"))
        # Bishops
        board.set_piece(COLUMN_BISHOPS, BLACK_KING_ROW, Piece("B", "b"))
        board.set_piece(COLUMN_BISHOPS, BLACK_QUEEN_ROW, Piece("B", "b"))
        # Queen
        board.set_piece("d", BLACK_QUEEN_ROW, Piece("Q", "b"))
        # King
        board.set_piece("d", BLACK_KING_ROW, Piece("K", "b"))

        # All pawns
        for col in COLUMNS:
            for row in WHITE_PAWNS_ROWS:
                board.set_piece(col, row, Piece("P", "w"))

            for row in BLACK_PAWNS_ROWS:
                board.set_piece(col, row, Piece("P", "b"))

    def __init__(self):
        """
        Initializes the game with a board and a piece list.
        """
        self.board = Board()
        self.fill_pieces(self.board)

    @staticmethod
    def _col_to_idx(col: str) -> int:
        """Convert a column letter to its index in COLUMNS.
        Parameters:
            col : str
        """
        return COLUMNS.index(col)

    @staticmethod
    def _idx_to_col(idx: int) -> str:
        """Convert an index to its corresponding column letter.
        Parameters:
            idx : int.
        """
        return COLUMNS[idx]

    @staticmethod
    def _wrap_row(row: int) -> int:
        """Wrap a row value into [1..16]
        Parameters:
            row : int
        """
        return (row - 1) % NUM_ROWS + 1

    @staticmethod
    def _phase_row(row: int) -> int:
        """Return the Mobius mirror row.
        Parameters:
            row : int
        """
        return 17 - row

    def get_valid_squares(self, col: str, row: int) -> list:
        """
        Returns every Square that the piece on (col, row) may legally move to
        this turn, including phase moves but not the piece's own square.

        Mobius rules:
        - Rows are cyclic: after row 16 comes row 1 (and vice-versa).
        - Phase move: (col, row) -> (col, 17-row), only if that square is empty.
        - Sliding pieces (R, B, Q) follow cyclic rows; blocked by own pieces,
          can capture enemy pieces but not slide past them.
        - Knight/King offsets use cyclic row wrapping; column stays in [a-d].
        - Pawns move one step forward cyclically (white: +1, black: -1),
          capture one step diagonally forward.
        """
        piece = self.board.get_piece(col, row)
        if piece is None:
            return []

        match piece.type:
            case "R":
                squares = self._rook_moves(col, row, piece.color)
            case "N":
                squares = self._knight_moves(col, row, piece.color)
            case "B":
                squares = self._bishop_moves(col, row, piece.color)
            case "Q":
                squares = self._queen_moves(col, row, piece.color)
            case "K":
                squares = self._king_moves(col, row, piece.color)
            case "P":
                squares = self._pawn_moves(col, row, piece.color)
            case _:
                squares = []

        squares += self._phase_moves(col, row)

        seen: set = set()
        unique = []
        for sq in squares:
            key = (sq.column, sq.row)
            if key not in seen:
                seen.add(key)
                unique.append(sq)

        return unique

    def _phase_moves(self, col: str, row: int) -> list:
        """Phase: teleport to the mirrored square if it is empty."""
        pr = self._phase_row(row)
        if self.board.get_piece(col, pr) is None:
            return [self.board.get_square(col, pr)]

        return []

    def _slide(
        self, col: str, row: int, color: str, col_delta: int, row_delta: int
    ) -> list:
        """
        Slide from (col, row) one step at a time in (col_delta, row_delta).

        col_delta in {-1, 0, 1}, row_delta in {-1, 0, 1}.

        Max steps:
          - Pure horizontal (row_delta == 0): NUM_COLS - 1
          - Otherwise: NUM_ROWS - 1  (avoids lapping back to start)

        Stops at/before a friendly piece; includes an enemy square (capture).
        """
        results = []
        seen: set = set()
        c_idx = self._col_to_idx(col)
        r = row

        max_steps = (NUM_COLS - 1) if row_delta == 0 else (NUM_ROWS - 1)

        for _ in range(max_steps):
            c_idx += col_delta
            r = self._wrap_row(r + row_delta)

            if c_idx < 0 or c_idx >= NUM_COLS:
                break

            target_col = self._idx_to_col(c_idx)
            key = (target_col, r)
            if key in seen:
                break

            seen.add(key)

            target_piece = self.board.get_piece(target_col, r)
            if target_piece is None:
                results.append(self.board.get_square(target_col, r))

            elif target_piece.color != color:
                results.append(self.board.get_square(target_col, r))
                break

            else:
                break  # friendly piece blocks

        return results

    def _rook_moves(self, col: str, row: int, color: str) -> list:
        results = []
        for dc, dr in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            results += self._slide(col, row, color, dc, dr)

        return results

    def _bishop_moves(self, col: str, row: int, color: str) -> list:
        results = []
        for dc, dr in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            results += self._slide(col, row, color, dc, dr)

        return results

    def _queen_moves(self, col: str, row: int, color: str) -> list:
        return self._rook_moves(col, row, color) + self._bishop_moves(col, row, color)

    def _knight_moves(self, col: str, row: int, color: str) -> list:
        """
        Standard knight offsets (±1,±2) and (±2,±1).
        Rows wrap cyclically; columns must stay within [a-d].
        """
        results = []
        c_idx = self._col_to_idx(col)
        for dc, dr in [
            (1, 2),
            (1, -2),
            (-1, 2),
            (-1, -2),
            (2, 1),
            (2, -1),
            (-2, 1),
            (-2, -1),
        ]:
            new_c = c_idx + dc
            new_r = self._wrap_row(row + dr)
            if new_c < 0 or new_c >= NUM_COLS:
                continue

            target_col = self._idx_to_col(new_c)
            target_piece = self.board.get_piece(target_col, new_r)
            if target_piece is None or target_piece.color != color:
                results.append(self.board.get_square(target_col, new_r))

        return results

    def _king_moves(self, col: str, row: int, color: str) -> list:
        """One step in any of the 8 directions; rows wrap, columns bounded."""
        results = []
        c_idx = self._col_to_idx(col)
        for dc, dr in [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ]:
            new_c = c_idx + dc
            new_r = self._wrap_row(row + dr)
            if new_c < 0 or new_c >= NUM_COLS:
                continue

            target_col = self._idx_to_col(new_c)
            target_piece = self.board.get_piece(target_col, new_r)
            if target_piece is None or target_piece.color != color:
                results.append(self.board.get_square(target_col, new_r))

        return results

    def _pawn_moves(self, col: str, row: int, color: str) -> list:
        """
        Forward one step (no capture); diagonal one step (capture only).
        White moves +1 (toward row 16 then wraps), Black moves -1.
        """
        direction = 1 if color == "w" else -1
        results = []
        c_idx = self._col_to_idx(col)

        # Forward (no capture)
        forward_r = self._wrap_row(row + direction)
        if self.board.get_piece(col, forward_r) is None:
            results.append(self.board.get_square(col, forward_r))

        # Diagonal captures
        for dc in (-1, 1):
            new_c = c_idx + dc
            if new_c < 0 or new_c >= NUM_COLS:
                continue

            diag_col = self._idx_to_col(new_c)
            diag_r = self._wrap_row(row + direction)
            target_piece = self.board.get_piece(diag_col, diag_r)
            if target_piece is not None and target_piece.color != color:
                results.append(self.board.get_square(diag_col, diag_r))

        return results


# tests
if __name__ == "__main__":
    board = Board()
    print(board)

    board.set_piece("c", 2, Piece("P", "w"))
    print(board.get_piece("c", 2))

    game = Game()
    print(game.board)
