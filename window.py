
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QMainWindow, QApplication, QToolBar
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

        self.hanoi_scene = HanoiScene(self.potter)

        toolbar = QToolBar("Movimientos", self)
        self.addToolBar(toolbar)

        undo_action = QAction("⟲ Deshacer", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.hanoi_scene.undo_move)
        toolbar.addAction(undo_action)

        redo_action = QAction("⟳ Rehacer", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.hanoi_scene.redo_move)
        toolbar.addAction(redo_action)

    def closeEvent(self, event):
        if hasattr(self, "hanoi_scene") and hasattr(self.hanoi_scene, "gestos"):
            self.hanoi_scene.gestos.stop()
            self.hanoi_scene._cursor_timer.stop()
        super().closeEvent(event)
        
    