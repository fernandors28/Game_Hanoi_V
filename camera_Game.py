import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PyQt6.QtCore  import QObject, QTimer,  pyqtSignal
import math
import cv2

class ControlGesto(QObject):
    event_mouse = pyqtSignal(str, int, int)
    def init__(self):
        self.tasks = mp.tasks
        self.model_path = "hand_landmarker.task"

        optionBase = python.BaseOptions(model_asset=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options = optionBase,
            running_mode = vision.RunningMode.IMAGE,
            num_hands = 1
        )
        self.detector =  vision.HandLandmarker.create_from_options(options)
        self.cap = cv2.VideoCapture(0)