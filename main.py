# --- Constants ---------------------------------------------------------------
COLUMNS = ["a", "b", "c", "d"]
NUM_COLS = len(COLUMNS)
NUM_ROWS = 16
ROWS = list(range(1, NUM_ROWS + 1))

COLUMN_ROOKS = "a"
COLUMN_KNIGHTS = "b"
COLUMN_BISHOPS = "c"

WHITE_QUEEN_ROW = 1
WHITE_KING_ROW = 16
BLACK_QUEEN_ROW = 16  # mirrored on a 16-row board
BLACK_KING_ROW = 1

WHITE_PAWNS_ROWS = [2, 3]
BLACK_PAWNS_ROWS = [14, 15]


class Square:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.piece = None

    def get_piece(self):
        return self.piece

    def set_piece(self, pce):
        self.piece = pce

    def __repr__(self):
        return f"Square({self.column}, {self.row}, {self.piece})"


class Board:
    """
    Represents the Möbius chess board.
    Rows 1, 2, 15, 16 are the starting rows (white queen-side on row 1,
    white king-side on row 16).
    """

    def __init__(self):
        self.board = [[Square(row, col) for col in COLUMNS] for row in ROWS]

    def set_piece(self, col, row, piece):
        self.board[row - 1][COLUMNS.index(col)].set_piece(piece)

    def get_piece(self, col, row):
        return self.board[row - 1][COLUMNS.index(col)].get_piece()

    def get_square(self, col, row) -> "Square":
        return self.board[row - 1][COLUMNS.index(col)]

    def __repr__(self):
        return str(self.board)


class Piece:
    def __init__(self, type, color):
        self.type = type
        self.color = color
        self.has_moved = False

    def __repr__(self):
        return f"Piece({self.type}, {self.color})"


class Game:
    """Represents the game of Möbius chess."""

    def __init__(self):
        self.board = Board()
        self.fill_pieces(self.board)
        # (col, row) of the pawn that just made a double push; None otherwise.
        self._en_passant_target: tuple | None = None

    def fill_pieces(self, board):
        """Fill the board with pieces in their starting positions."""
        # White back ranks
        for row in (WHITE_QUEEN_ROW, WHITE_KING_ROW):
            board.set_piece(COLUMN_ROOKS, row, Piece("R", "w"))
            board.set_piece(COLUMN_KNIGHTS, row, Piece("N", "w"))
            board.set_piece(COLUMN_BISHOPS, row, Piece("B", "w"))
        board.set_piece("d", WHITE_QUEEN_ROW, Piece("Q", "w"))
        board.set_piece("d", WHITE_KING_ROW, Piece("K", "w"))

        # Black back ranks
        for row in (BLACK_QUEEN_ROW, BLACK_KING_ROW):
            board.set_piece(COLUMN_ROOKS, row, Piece("R", "b"))
            board.set_piece(COLUMN_KNIGHTS, row, Piece("N", "b"))
            board.set_piece(COLUMN_BISHOPS, row, Piece("B", "b"))
        board.set_piece("d", BLACK_QUEEN_ROW, Piece("Q", "b"))
        board.set_piece("d", BLACK_KING_ROW, Piece("K", "b"))

        # Pawns
        for col in COLUMNS:
            for row in WHITE_PAWNS_ROWS:
                board.set_piece(col, row, Piece("P", "w"))
            for row in BLACK_PAWNS_ROWS:
                board.set_piece(col, row, Piece("P", "b"))

    @staticmethod
    def _col_to_idx(col: str) -> int:
        return COLUMNS.index(col)

    @staticmethod
    def _idx_to_col(idx: int) -> str:
        return COLUMNS[idx]

    @staticmethod
    def _wrap_row(row: int) -> int:
        return (row - 1) % NUM_ROWS + 1

    @staticmethod
    def _phase_row(row: int) -> int:
        return 17 - row

    def get_valid_squares(self, col: str, row: int) -> list:
        """
        Returns every Square the piece on (col, row) may legally move to,
        including phase moves, castling, and en-passant.
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

    def move(self, base_col: str, base_row: int, new_col: str, new_row: int) -> bool:
        """
        Move the piece on (base_col, base_row) to (new_col, new_row).

        Validates against get_valid_squares.  Handles:
          • Normal moves and captures.
          • En-passant capture (removes the captured pawn from the board).
          • Castling (moves the rook to its post-castle square).
          • Double pawn push tracking (updates _en_passant_target).
          • Marking every moved piece with has_moved = True.

        Returns True if the move was legal and applied; False otherwise
        (board is left unchanged on failure).
        """
        piece = self.board.get_piece(base_col, base_row)
        if piece is None:
            return False

        valid_squares = self.get_valid_squares(base_col, base_row)
        if not any(sq.column == new_col and sq.row == new_row for sq in valid_squares):
            return False

        # En-passant ?
        # Detect before resetting _en_passant_target.
        ep_capture_pos: tuple | None = None
        if piece.type == "P" and self._en_passant_target is not None:
            ep_col, ep_row = self._en_passant_target
            direction = 1 if piece.color == "w" else -1
            ep_landing_row = self._wrap_row(ep_row + direction)
            if new_col == ep_col and new_row == ep_landing_row:
                ep_capture_pos = (ep_col, ep_row)

        # Castling ?
        castle_rook_from: tuple | None = None
        castle_rook_to: tuple | None = None
        if piece.type == "K" and not piece.has_moved:
            col_delta = self._col_to_idx(new_col) - self._col_to_idx(base_col)
            if abs(col_delta) == 2:
                if col_delta > 0:  # kingside  (→)
                    castle_rook_from = (COLUMNS[-1], base_row)
                    castle_rook_to = (COLUMNS[self._col_to_idx(new_col) - 1], base_row)
                else:  # queenside (←)
                    castle_rook_from = (COLUMNS[0], base_row)
                    castle_rook_to = (COLUMNS[self._col_to_idx(new_col) + 1], base_row)

        # Apply
        self.board.set_piece(base_col, base_row, None)
        self.board.set_piece(new_col, new_row, piece)
        piece.has_moved = True

        if ep_capture_pos is not None:
            self.board.set_piece(ep_capture_pos[0], ep_capture_pos[1], None)

        if castle_rook_from is not None:
            rook = self.board.get_piece(*castle_rook_from)
            self.board.set_piece(castle_rook_from[0], castle_rook_from[1], None)
            self.board.set_piece(castle_rook_to[0], castle_rook_to[1], rook)
            if rook is not None:
                rook.has_moved = True

        # Update en-passant target
        row_delta = new_row - base_row
        cyclic_delta = (row_delta + NUM_ROWS // 2) % NUM_ROWS - NUM_ROWS // 2
        if piece.type == "P" and abs(cyclic_delta) == 2:
            self._en_passant_target = (new_col, new_row)
        else:
            self._en_passant_target = None

        return True

    def _phase_moves(self, col: str, row: int) -> list:
        """Teleport to the Möbius mirror square if it is empty."""
        pr = self._phase_row(row)
        if self.board.get_piece(col, pr) is None:
            return [self.board.get_square(col, pr)]
        return []

    def _slide(
        self, col: str, row: int, color: str, col_delta: int, row_delta: int
    ) -> list:
        """Slide in one direction until blocked."""
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
                break
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
        """One step in any direction plus castling (when eligible)."""
        results = []
        c_idx = self._col_to_idx(col)
        piece = self.board.get_piece(col, row)

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

        if piece is not None and not piece.has_moved:
            results += self._castling_moves(col, row, color)

        return results

    def _castling_moves(self, col: str, row: int, color: str) -> list:
        """
        Return castling destination squares for the king on (col, row).

        For each horizontal direction:
          1. Walk outward; the first piece found must be an unmoved friendly rook.
          2. Every square strictly between king and rook must be empty.
          3. King must have two free columns to slide into (king_dest = col ± 2).
        """
        results = []
        k_idx = self._col_to_idx(col)

        for direction in (-1, 1):
            # Find the first piece outward in this direction
            rook_idx = None
            step = k_idx + direction
            while 0 <= step < NUM_COLS:
                candidate = self.board.get_piece(self._idx_to_col(step), row)
                if candidate is not None:
                    if (
                        candidate.type == "R"
                        and candidate.color == color
                        and not candidate.has_moved
                    ):
                        rook_idx = step
                    break  # any piece stops the search
                step += direction

            if rook_idx is None:
                continue

            # Path between king and rook must be clear
            lo = min(k_idx + direction, rook_idx)
            hi = max(k_idx + direction, rook_idx)
            path_clear = all(
                self.board.get_piece(self._idx_to_col(i), row) is None
                for i in range(lo, hi + 1)
                if i != k_idx and i != rook_idx
            )
            if not path_clear:
                continue

            king_dest_idx = k_idx + 2 * direction
            if king_dest_idx < 0 or king_dest_idx >= NUM_COLS:
                continue

            results.append(self.board.get_square(self._idx_to_col(king_dest_idx), row))

        return results

    def _pawn_moves(self, col: str, row: int, color: str) -> list:
        """
        Forward one step; double push from starting rank; diagonal capture;
        en-passant capture.
        """
        direction = 1 if color == "w" else -1
        results = []
        c_idx = self._col_to_idx(col)
        forward_r = self._wrap_row(row + direction)
        starting_rows = WHITE_PAWNS_ROWS if color == "w" else BLACK_PAWNS_ROWS

        # Single step forward
        if self.board.get_piece(col, forward_r) is None:
            results.append(self.board.get_square(col, forward_r))

            # Double push from starting rank (only when single step is clear)
            if row in starting_rows:
                double_r = self._wrap_row(row + 2 * direction)
                if self.board.get_piece(col, double_r) is None:
                    results.append(self.board.get_square(col, double_r))

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

        # En-passant capture
        if self._en_passant_target is not None:
            ep_col, ep_row = self._en_passant_target
            if ep_row == row and abs(self._col_to_idx(ep_col) - c_idx) == 1:
                ep_landing_row = self._wrap_row(ep_row + direction)
                results.append(self.board.get_square(ep_col, ep_landing_row))

        return results


if __name__ == "__main__":
    # helpers
    def sq(squares):
        """Return a sorted list of (col, row) from a list of Squares."""
        return sorted((s.column, s.row) for s in squares)

    def empty():
        """Return a Game with a completely empty board."""
        g = Game()
        g.board = Board()
        g._en_passant_target = None
        return g

    # 1. board basics
    print("=== 1. Board basics ===")

    board = Board()
    print(board)  # empty 16-row board

    board.set_piece("c", 2, Piece("P", "w"))
    print(board.get_piece("c", 2))  # Piece(P, w)

    board.set_piece("c", 2, None)
    print(board.get_piece("c", 2))  # None  (cleared)

    game = Game()
    print(game.board)  # fully populated board

    # 2. game starting pos
    print("\n=== 2. Game starting position ===")

    game = Game()
    print(game.board.get_piece("d", BLACK_KING_ROW))  # Piece(K, b)
    print(game.board.get_piece("d", BLACK_QUEEN_ROW))  # Piece(Q, b)
    print(game.board.get_piece("a", 2))  # Piece(P, w)  white pawn
    print(game.board.get_piece("a", 15))  # Piece(P, b)  black pawn
    print(game.board.get_piece("a", 8))  # None         mid-board empty

    # 3. Phase moves
    print("\n=== 3. Phase moves ===")

    g = empty()
    g.board.set_piece("a", 5, Piece("R", "w"))
    print(sq(g.get_valid_squares("a", 5)))  # includes ('a', 12)  [phase(5)=12]

    # Phase blocked by occupant
    g2 = empty()
    g2.board.set_piece("c", 8, Piece("B", "w"))  # bishop; phase(8)=9
    g2.board.set_piece("c", 9, Piece("P", "b"))  # occupies mirror square
    print(("c", 9) in sq(g2.get_valid_squares("c", 8)))  # False - phase blocked

    # move() via phase
    g3 = empty()
    g3.board.set_piece("b", 3, Piece("R", "w"))
    print(g3.move("b", 3, "b", 14))  # True  [phase(3)=14]
    print(g3.board.get_piece("b", 14))  # Piece(R, w)
    print(g3.board.get_piece("b", 3))  # None

    # 4. Rook moves
    print("\n=== 4. Rook moves ===")

    g = empty()
    g.board.set_piece("b", 5, Piece("R", "w"))
    print(sq(g.get_valid_squares("b", 5)))  # all reachable squares

    # Friendly blocks horizontal slide
    g2 = empty()
    g2.board.set_piece("a", 5, Piece("R", "w"))
    g2.board.set_piece("c", 5, Piece("P", "w"))  # friendly at c5
    valid = sq(g2.get_valid_squares("a", 5))
    print(("b", 5) in valid)  # True  - one step right is fine
    print(("c", 5) in valid)  # False - friendly blocker
    print(("d", 5) in valid)  # False - hidden behind blocker

    # Enemy capture: rook can land on enemy but not slide past
    g3 = empty()
    g3.board.set_piece("a", 5, Piece("R", "w"))
    g3.board.set_piece("a", 7, Piece("P", "b"))
    valid3 = sq(g3.get_valid_squares("a", 5))
    print(("a", 7) in valid3)  # True  - capture
    print(g3.move("a", 5, "a", 7))  # True
    print(g3.board.get_piece("a", 7))  # Piece(R, w)

    # Row wrap: rook at a2 can reach a16 by going downward
    g4 = empty()
    g4.board.set_piece("a", 2, Piece("R", "w"))
    print(("a", 16) in sq(g4.get_valid_squares("a", 2)))  # True  - cyclic wrap

    # 5. Bishop moves
    print("\n=== 5. Bishop moves ===")

    g = empty()
    g.board.set_piece("a", 1, Piece("B", "w"))
    print(sq(g.get_valid_squares("a", 1)))  # diagonals + phase

    # Diagonal blocked by friendly
    g2 = empty()
    g2.board.set_piece("b", 5, Piece("B", "w"))
    g2.board.set_piece("c", 6, Piece("P", "w"))  # blocks (1,1) diagonal
    valid2 = sq(g2.get_valid_squares("b", 5))
    print(("c", 6) in valid2)  # False - friendly
    print(("d", 7) in valid2)  # False - hidden

    # Enemy on diagonal: can capture, cannot slide past
    g3 = empty()
    g3.board.set_piece("b", 5, Piece("B", "w"))
    g3.board.set_piece("c", 6, Piece("P", "b"))
    valid3 = sq(g3.get_valid_squares("b", 5))
    print(("c", 6) in valid3)  # True  - capture
    print(("d", 7) in valid3)  # False - past enemy

    # 6. Knight moves
    print("\n=== 6. Knight moves ===")

    g = empty()
    g.board.set_piece("b", 5, Piece("N", "w"))
    print(sq(g.get_valid_squares("b", 5)))  # all L-shaped targets

    # Row wrap: knight at b1, offsets of -2 wrap to row 15/16
    g2 = empty()
    g2.board.set_piece("b", 1, Piece("N", "w"))
    valid2 = sq(g2.get_valid_squares("b", 1))
    print(("a", 15) in valid2)  # True  - wrap
    print(("c", 15) in valid2)  # True  - wrap

    # Cannot land on friendly
    g3 = empty()
    g3.board.set_piece("b", 5, Piece("N", "w"))
    g3.board.set_piece("c", 7, Piece("P", "w"))
    print(("c", 7) in sq(g3.get_valid_squares("b", 5)))  # False - friendly

    # Can capture enemy
    g4 = empty()
    g4.board.set_piece("b", 5, Piece("N", "w"))
    g4.board.set_piece("c", 7, Piece("P", "b"))
    print(("c", 7) in sq(g4.get_valid_squares("b", 5)))  # True  - enemy capture

    # 7. King moves
    print("\n=== 7. King moves ===")

    g = empty()
    g.board.set_piece("b", 5, Piece("K", "w"))
    print(sq(g.get_valid_squares("b", 5)))  # 8 directions + phase

    # Cannot step on friendly
    g2 = empty()
    g2.board.set_piece("b", 5, Piece("K", "w"))
    g2.board.set_piece("c", 5, Piece("P", "w"))
    print(("c", 5) in sq(g2.get_valid_squares("b", 5)))  # False - friendly

    # Can step on enemy
    g3 = empty()
    g3.board.set_piece("b", 5, Piece("K", "w"))
    g3.board.set_piece("c", 5, Piece("P", "b"))
    print(("c", 5) in sq(g3.get_valid_squares("b", 5)))  # True  - enemy

    # 8. Pawn moves
    print("\n=== 8. Pawn moves ===")

    # White moves forward (+1)
    g = empty()
    g.board.set_piece("a", 5, Piece("P", "w"))
    print(sq(g.get_valid_squares("a", 5)))  # a6 + phase(a,12)

    # Black moves forward (-1)
    g2 = empty()
    g2.board.set_piece("a", 10, Piece("P", "b"))
    print(sq(g2.get_valid_squares("a", 10)))  # a9 + phase(a,7)

    # Double push from white starting rank
    g3 = empty()
    g3.board.set_piece("a", 2, Piece("P", "w"))
    valid3 = sq(g3.get_valid_squares("a", 2))
    print(("a", 3) in valid3)  # True
    print(("a", 4) in valid3)  # True  - double push

    # Double push blocked when first square is occupied
    g4 = empty()
    g4.board.set_piece("a", 2, Piece("P", "w"))
    g4.board.set_piece("a", 3, Piece("P", "b"))
    valid4 = sq(g4.get_valid_squares("a", 2))
    print(("a", 3) in valid4)  # False - blocked
    print(("a", 4) in valid4)  # False - can't skip

    # Double push blocked only on second square: single step still valid
    g5 = empty()
    g5.board.set_piece("a", 2, Piece("P", "w"))
    g5.board.set_piece("a", 4, Piece("R", "b"))
    valid5 = sq(g5.get_valid_squares("a", 2))
    print(("a", 3) in valid5)  # True  - single step OK
    print(("a", 4) in valid5)  # False - blocked

    # Diagonal capture: enemy yes, friendly no, empty no
    g6 = empty()
    g6.board.set_piece("b", 5, Piece("P", "w"))
    g6.board.set_piece("a", 6, Piece("P", "b"))  # enemy - capturable
    g6.board.set_piece("c", 6, Piece("P", "w"))  # friendly - not capturable
    valid6 = sq(g6.get_valid_squares("b", 5))
    print(("a", 6) in valid6)  # True
    print(("c", 6) in valid6)  # False

    # Pawn blocked forward - cannot move at all (only phase)
    g7 = empty()
    g7.board.set_piece("a", 5, Piece("P", "w"))
    g7.board.set_piece("a", 6, Piece("N", "w"))  # friendly blocks
    valid7 = sq(g7.get_valid_squares("a", 5))
    print(("a", 6) in valid7)  # False
    print(("a", 12) in valid7)  # True  - only phase left

    # Wrap: white pawn at row 16 steps to row 1
    g8 = empty()
    g8.board.set_piece("a", 16, Piece("P", "w"))
    print(("a", 1) in sq(g8.get_valid_squares("a", 16)))  # True  - cyclic wrap

    # No double push outside starting ranks
    g9 = empty()
    g9.board.set_piece("a", 5, Piece("P", "w"))
    print(("a", 7) in sq(g9.get_valid_squares("a", 5)))  # False

    # 9. En-passant
    print("\n=== 9. En-passant ===")

    # Double push sets the EP target
    g = empty()
    g.board.set_piece("b", 2, Piece("P", "w"))
    g.move("b", 2, "b", 4)
    print(g._en_passant_target)  # ('b', 4)

    # Single push clears any existing EP target
    g2 = empty()
    g2.board.set_piece("b", 5, Piece("P", "w"))
    g2._en_passant_target = ("a", 5)
    g2.move("b", 5, "b", 6)
    print(g2._en_passant_target)  # None

    # EP landing square appears for adjacent pawn
    g3 = empty()
    g3.board.set_piece("b", 4, Piece("P", "w"))  # will capture
    g3.board.set_piece("c", 4, Piece("P", "b"))  # just double-pushed
    g3._en_passant_target = ("c", 4)
    print(("c", 5) in sq(g3.get_valid_squares("b", 4)))  # True  - EP landing

    # EP capture removes the victim pawn from its own square
    g4 = empty()
    g4.board.set_piece("b", 4, Piece("P", "w"))
    g4.board.set_piece("c", 4, Piece("P", "b"))
    g4._en_passant_target = ("c", 4)
    print(g4.move("b", 4, "c", 5))  # True
    print(g4.board.get_piece("c", 4))  # None  - victim removed
    print(g4.board.get_piece("c", 5))  # Piece(P, w)

    # EP expires after one turn
    g5 = empty()
    g5.board.set_piece("a", 12, Piece("P", "w"))  # potential capturer
    g5.board.set_piece("b", 14, Piece("P", "b"))  # will double push
    g5.move("b", 14, "b", 12)
    print(g5._en_passant_target)  # ('b', 12)
    g5.move("a", 12, "a", 13)  # white plays elsewhere
    print(g5._en_passant_target)  # None  - window closed

    # Black pawn performs EP capture on white
    g6 = empty()
    g6.board.set_piece("c", 13, Piece("P", "b"))  # black capturer
    g6.board.set_piece("b", 13, Piece("P", "w"))  # white victim
    g6._en_passant_target = ("b", 13)
    print(g6.move("c", 13, "b", 12))  # True  [landing=b13+(-1)=b12]
    print(g6.board.get_piece("b", 13))  # None  - white pawn removed
    print(g6.board.get_piece("b", 12))  # Piece(P, b)

    # 10. Castling
    print("\n=== 10. Castling ===")

    # Queenside castle available when path is clear and neither piece has moved
    g = empty()
    g.board.set_piece("d", 5, Piece("K", "w"))
    g.board.set_piece("a", 5, Piece("R", "w"))  # b5 and c5 are empty
    print(("b", 5) in sq(g.get_valid_squares("d", 5)))  # True  - castle destination

    # Castling executes: king to b5, rook to c5
    g2 = empty()
    king = Piece("K", "w")
    rook = Piece("R", "w")
    g2.board.set_piece("d", 5, king)
    g2.board.set_piece("a", 5, rook)
    print(g2.move("d", 5, "b", 5))  # True
    print(g2.board.get_piece("b", 5))  # Piece(K, w)
    print(g2.board.get_piece("c", 5))  # Piece(R, w)
    print(g2.board.get_piece("d", 5))  # None
    print(g2.board.get_piece("a", 5))  # None
    print(king.has_moved, rook.has_moved)  # True True

    # Castling blocked by piece in path
    g3 = empty()
    g3.board.set_piece("d", 5, Piece("K", "w"))
    g3.board.set_piece("a", 5, Piece("R", "w"))
    g3.board.set_piece("b", 5, Piece("N", "w"))  # blocks the path
    print(("b", 5) in sq(g3.get_valid_squares("d", 5)))  # False - no castling

    # Castling blocked when king has already moved
    g4 = empty()
    moved_king = Piece("K", "w")
    moved_king.has_moved = True
    g4.board.set_piece("d", 5, moved_king)
    g4.board.set_piece("a", 5, Piece("R", "w"))
    print(("b", 5) in sq(g4.get_valid_squares("d", 5)))  # False - king moved

    # Castling blocked when rook has already moved
    g5 = empty()
    moved_rook = Piece("R", "w")
    moved_rook.has_moved = True
    g5.board.set_piece("d", 5, Piece("K", "w"))
    g5.board.set_piece("a", 5, moved_rook)
    print(("b", 5) in sq(g5.get_valid_squares("d", 5)))  # False - rook moved

    # 11. move() validation
    print("\n=== 11. move() validation ===")

    # Empty origin
    g = empty()
    print(g.move("a", 5, "a", 6))  # False - no piece there

    # Same square
    g2 = empty()
    g2.board.set_piece("a", 5, Piece("R", "w"))
    print(g2.move("a", 5, "a", 5))  # False

    # Friendly on destination
    g3 = empty()
    g3.board.set_piece("a", 5, Piece("R", "w"))
    g3.board.set_piece("b", 5, Piece("P", "w"))
    print(g3.move("a", 5, "b", 5))  # False

    # Board unchanged after failed move
    g4 = empty()
    rook = Piece("R", "w")
    pawn = Piece("P", "w")
    g4.board.set_piece("a", 5, rook)
    g4.board.set_piece("b", 5, pawn)
    g4.move("a", 5, "b", 5)
    print(g4.board.get_piece("a", 5))  # Piece(R, w) - untouched
    print(g4.board.get_piece("b", 5))  # Piece(P, w) - untouched

    # Piece marked as moved after successful move
    g5 = empty()
    p = Piece("R", "w")
    g5.board.set_piece("a", 5, p)
    g5.move("a", 5, "b", 5)
    print(p.has_moved)  # True

    # Origin cleared after move
    g6 = empty()
    g6.board.set_piece("a", 5, Piece("R", "w"))
    g6.move("a", 5, "b", 5)
    print(g6.board.get_piece("a", 5))  # None

    # 12. Multi-step scenarios
    print("\n=== 12. Multi-step scenarios ===")

    # Rook moves across the board in two steps
    g = empty()
    g.board.set_piece("a", 1, Piece("R", "w"))
    g.move("a", 1, "a", 8)
    g.move("a", 8, "d", 8)
    print(g.board.get_piece("d", 8))  # Piece(R, w)
    print(g.board.get_piece("a", 1))  # None
    print(g.board.get_piece("a", 8))  # None

    # Knight phases to mirror row, then phases back
    g2 = empty()
    g2.board.set_piece("b", 5, Piece("N", "w"))
    g2.move("b", 5, "b", 12)  # phase(5)=12
    print(g2.board.get_piece("b", 12))  # Piece(N, w)
    g2.move("b", 12, "b", 5)  # phase(12)=5
    print(g2.board.get_piece("b", 5))  # Piece(N, w)
    print(g2.board.get_piece("b", 12))  # None

    # Pawn diagonal capture in sequence
    g3 = empty()
    g3.board.set_piece("b", 5, Piece("P", "w"))
    g3.board.set_piece("c", 6, Piece("P", "b"))
    print(g3.move("b", 5, "c", 6))  # True  - diagonal capture
    print(g3.board.get_piece("c", 6))  # Piece(P, w)
    print(g3.board.get_piece("b", 5))  # None
