
from PyQt6.QtWidgets import QMainWindow, QApplication
from pyvistaqt import QtInteractor
from Hanoi import HanoiScene
import sys
import os


os.environ["QT_QPA_PLATFORM"] = "xcb"

# Desactivar avisos de renderizado de VTK en consola o interfaz
os.environ["VTK_SILENT"] = "1"

class Window_Game(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Torre de Hanoi")
        self.status_game = False

        self.potter = QtInteractor(self)
        self.potter.enable_custom_trackball_style(
            left='pan',
            shift_left='pan',
            control_left='pan',
            middle='pan',
            shift_middle='pan',
            control_middle='pan',
            right='dolly',
            shift_right='dolly',
            control_right='dolly',
        )
        self.setCentralWidget(self.potter)
        self.showMaximized()

        HanoiScene(self.potter)
        
    