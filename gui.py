from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLayout
)
from main import Game, Board, Piece


class MainWindow(QMainWindow):
    def __init__(self, game:Game = None, debug:bool = False):
        super().__init__()
        self.game = game
        self.debug = debug

        self.init_views()

    def init_views(self):
        self.board_view = BoardView(self, self.debug)


class BoardView(QWidget):
    def __init__(self, main:MainWindow = None, debug:bool = False):
        super().__init__()
        self.main = main
        self.debug = debug

        self.hide()

    def display_circular_board(self):
        board = self.main.game.get_board()