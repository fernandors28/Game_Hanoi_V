
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QStackedWidget,
    QStackedLayout,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
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
        self.statusBar()

        self.scene_container = QWidget(self)
        self.scene_layout = QStackedLayout(self.scene_container)
        self.scene_layout.setContentsMargins(0, 0, 0, 0)
        self.scene_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)

        self.potter = QtInteractor(self.scene_container)
        self.scene_layout.addWidget(self.potter)
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
        self.setCentralWidget(self.scene_container)
        self.showMaximized()

        self.hanoi_scene = HanoiScene(self.potter, self._show_gripper_status)

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

        self.undo_action = undo_action
        self.redo_action = redo_action

        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    def eventFilter(self, watched, event):
        if (
            event.type() == QEvent.Type.KeyPress
            and event.key() == Qt.Key.Key_Escape
            and self.isActiveWindow()
        ):
            self._toggle_pause_menu()
            return True
        return super().eventFilter(watched, event)

    def _toggle_pause_menu(self):
        if self.hanoi_scene.is_paused:
            self._resume_game()
            return

        self.hanoi_scene.pause()
        self.undo_action.setEnabled(False)
        self.redo_action.setEnabled(False)
        if not hasattr(self, "pause_overlay"):
            self._create_pause_overlay()

        self.pause_overlay.show()
        self.pause_overlay.raise_()

    def _create_pause_overlay(self):
        # Ambos widgets comparten un QStackedLayout para dibujar el menú sobre VTK.
        self.pause_overlay = QWidget(self.scene_container)
        self.scene_layout.addWidget(self.pause_overlay)
        self.pause_overlay.setObjectName("pauseOverlay")
        self.pause_overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.pause_overlay.setStyleSheet(
            """
            QWidget#pauseOverlay { background-color: rgba(15, 23, 42, 105); }
            QFrame#pausePanel {
                background-color: rgba(255, 255, 255, 245);
                border-radius: 16px;
            }
            QLabel#pauseTitle {
                color: #172033;
                font-size: 24px;
                font-weight: 700;
            }
            QLabel#pauseHint {
                color: #526078;
                font-size: 13px;
            }
            QPushButton {
                min-height: 42px;
                padding: 0 16px;
                border: 0;
                border-radius: 8px;
                background-color: #e8edf5;
                color: #172033;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #d7e1ef; }
            QPushButton#resumeButton {
                background-color: #2563eb;
                color: white;
                font-weight: 600;
            }
            QPushButton#resumeButton:hover { background-color: #1d4ed8; }
            """
        )

        overlay_layout = QVBoxLayout(self.pause_overlay)
        overlay_layout.setContentsMargins(16, 16, 16, 16)
        self.pause_pages = QStackedWidget(self.pause_overlay)
        self.pause_pages.setFixedWidth(340)
        overlay_layout.addStretch()
        overlay_layout.addWidget(
            self.pause_pages, alignment=Qt.AlignmentFlag.AlignCenter
        )
        overlay_layout.addStretch()

        pause_page = QFrame(self.pause_pages)
        pause_page.setObjectName("pausePanel")
        pause_layout = QVBoxLayout(pause_page)
        pause_layout.setContentsMargins(24, 24, 24, 24)
        pause_layout.setSpacing(12)

        title = QLabel("Juego en pausa", pause_page)
        title.setObjectName("pauseTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pause_layout.addWidget(title)

        resume_button = QPushButton("▶ Reanudar", pause_page)
        resume_button.setObjectName("resumeButton")
        resume_button.clicked.connect(lambda: self._resume_game())
        pause_layout.addWidget(resume_button)

        settings_button = QPushButton("⚙ Configuración", pause_page)
        settings_button.clicked.connect(lambda: self.pause_pages.setCurrentIndex(1))
        pause_layout.addWidget(settings_button)

        restart_button = QPushButton("↻ Reiniciar partida", pause_page)
        restart_button.clicked.connect(self._restart_from_pause)
        pause_layout.addWidget(restart_button)

        exit_button = QPushButton("Salir", pause_page)
        exit_button.clicked.connect(self.close)
        pause_layout.addWidget(exit_button)
        self.pause_pages.addWidget(pause_page)

        settings_page = QFrame(self.pause_pages)
        settings_page.setObjectName("pausePanel")
        settings_layout = QVBoxLayout(settings_page)
        settings_layout.setContentsMargins(24, 24, 24, 24)
        settings_layout.setSpacing(12)

        settings_title = QLabel("Configuración", settings_page)
        settings_title.setObjectName("pauseTitle")
        settings_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_layout.addWidget(settings_title)

        self.grab_threshold_label = QLabel(settings_page)
        self.grab_threshold_label.setObjectName("pauseHint")
        settings_layout.addWidget(self.grab_threshold_label)

        grab_threshold_slider = QSlider(Qt.Orientation.Horizontal, settings_page)
        grab_threshold_slider.setRange(4, 16)
        grab_threshold_slider.setValue(
            round(self.hanoi_scene.gestos.grab_threshold * 100)
        )
        grab_threshold_slider.valueChanged.connect(self._update_grab_threshold)
        settings_layout.addWidget(grab_threshold_slider)
        self._update_grab_threshold(grab_threshold_slider.value())

        self.cursor_sensitivity_label = QLabel(settings_page)
        self.cursor_sensitivity_label.setObjectName("pauseHint")
        settings_layout.addWidget(self.cursor_sensitivity_label)

        cursor_sensitivity_slider = QSlider(Qt.Orientation.Horizontal, settings_page)
        cursor_sensitivity_slider.setRange(20, 100)
        cursor_sensitivity_slider.setValue(
            round(self.hanoi_scene.config["cursor_sensitivity"] * 100)
        )
        cursor_sensitivity_slider.valueChanged.connect(self._update_cursor_sensitivity)
        settings_layout.addWidget(cursor_sensitivity_slider)
        self._update_cursor_sensitivity(cursor_sensitivity_slider.value())

        self.cursor_speed_label = QLabel(settings_page)
        self.cursor_speed_label.setObjectName("pauseHint")
        settings_layout.addWidget(self.cursor_speed_label)

        cursor_speed_slider = QSlider(Qt.Orientation.Horizontal, settings_page)
        cursor_speed_slider.setRange(50, 150)
        cursor_speed_slider.setValue(round(self.hanoi_scene.config["speed"] * 100))
        cursor_speed_slider.valueChanged.connect(self._update_cursor_speed)
        settings_layout.addWidget(cursor_speed_slider)
        self._update_cursor_speed(cursor_speed_slider.value())

        settings_layout.addWidget(
            QLabel("A mayor valor, el gesto de pinza se activa con más facilidad.", settings_page)
        )
        back_button = QPushButton("← Volver a pausa", settings_page)
        back_button.clicked.connect(lambda: self.pause_pages.setCurrentIndex(0))
        settings_layout.addWidget(back_button)
        self.pause_pages.addWidget(settings_page)
        self.pause_pages.setCurrentIndex(0)
        self.pause_overlay.hide()

    def _update_grab_threshold(self, value):
        threshold = value / 100.0
        self.hanoi_scene.gestos.grab_threshold = threshold
        self.grab_threshold_label.setText(f"Umbral de agarre: {threshold:.2f}")

    def _update_cursor_sensitivity(self, value):
        sensitivity = value / 100.0
        self.hanoi_scene.set_hand_config(cursor_sensitivity=sensitivity)
        self.cursor_sensitivity_label.setText(
            f"Sensibilidad del cursor: {sensitivity:.2f}"
        )

    def _update_cursor_speed(self, value):
        speed = value / 100.0
        self.hanoi_scene.set_hand_config(speed=speed)
        self.cursor_speed_label.setText(f"Rapidez del cursor: {speed:.2f}")

    def _restart_from_pause(self):
        self.hanoi_scene.reset_game()
        self._resume_game("Partida reiniciada")

    def _resume_game(self, message="Juego reanudado"):
        self.hanoi_scene.resume()
        self.undo_action.setEnabled(True)
        self.redo_action.setEnabled(True)
        self.pause_overlay.hide()
        self.statusBar().showMessage(message, 2000)

    def _show_gripper_status(self, is_grabbing):
        message = "Pinza ACTIVADA" if is_grabbing else "Pinza DESACTIVADA"
        self.statusBar().showMessage(message, 2000)

    def closeEvent(self, event):
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        if hasattr(self, "hanoi_scene") and hasattr(self.hanoi_scene, "gestos"):
            self.hanoi_scene.gestos.stop()
            self.hanoi_scene._cursor_timer.stop()
        super().closeEvent(event)
        
    