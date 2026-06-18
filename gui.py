from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLayout
)
from main import Game

class MainWindow(QMainWindow):
    def __init__(self, game:Game = None, debug:bool = False):
        super().__init__()
        self.game = game
        self.debug = debug