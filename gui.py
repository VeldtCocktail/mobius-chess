from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLayout
)

class MainWindow(QMainWindow):
    def __init__(self, game = None, debug = False):
        super().__init__()
        self.game = game
        self.debug = debug