import mediapipe as mp

from collections import deque
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PyQt6.QtCore  import QObject, QTimer,  pyqtSignal
import math
import cv2
import os

class ControlGesto(QObject):
    event_mano = pyqtSignal(float, float, bool)

    @staticmethod
    def _smooth_cursor_position(current, target, smoothing=0.35, dead_zone=0.1):
        if current is None:
            return target

        delta = tuple(target_i - current_i for current_i, target_i in zip(current, target))
        if max(abs(value) for value in delta) < dead_zone:
            return current

        return tuple(
            current_i + (target_i - current_i) * smoothing
            for current_i, target_i in zip(current, target)
        )

    def _update_grab_state(self, distance):
        self._grab_samples.append(distance)
        recent = list(self._grab_samples)
        latest = recent[-1]
        recent_max = max(recent)
        recent_min = min(recent)

        if self._grab_state:
            new_state = recent_max <= self.grab_open_threshold
        else:
            new_state = recent_min <= self.grab_close_threshold and latest <= self.grab_close_threshold

        self._grab_state = new_state
        return self._grab_state

    def __init__(
        self,
        x_min_3d,
        x_max_3d,
        z_min_3d,
        z_max_3d,
        cursor_smoothing=0.45,
        cursor_dead_zone=0.08,
        grab_close_threshold=0.12,
        grab_open_threshold=0.16,
        speed=1.0,
    ):
        super().__init__()
        self.x_min_3d = x_min_3d
        self.x_max_3d = x_max_3d
        self.z_min_3d = z_min_3d
        self.z_max_3d = z_max_3d
        self.cursor_smoothing = cursor_smoothing
        self.cursor_dead_zone = cursor_dead_zone
        self.grab_threshold = 0.08
        self.grab_close_threshold = grab_close_threshold
        self.grab_open_threshold = grab_open_threshold
        self.speed = speed
        self._filtered_target = None
        self._grab_state = False
        self._grab_samples = deque(maxlen=4)
           
        self.tasks = mp.tasks
        self.model_path = "hand_landmarker.task"

        optionBase = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options = optionBase,
            running_mode = vision.RunningMode.IMAGE,
            num_hands = 1
        )
        self.detector =  vision.HandLandmarker.create_from_options(options)
        self.cap = cv2.VideoCapture(0)
        self.timer =QTimer()
        self.timer.timeout.connect(self.procesar_frame)
  
    def start(self, fps=30):
        self.timer.start(1000 // fps)
    def stop(self):
        self.timer.stop()
        if self.cap.isOpened():
            self.cap.release()
    def procesar_frame(self):
        ret,frame = self.cap.read()
        if not ret:
            return
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        resultado = self.detector.detect(mp_img)
        if not resultado.hand_landmarks:
            return

        mano = resultado.hand_landmarks[0]
        pulgar = mano[4]
        indice = mano[8]

        x_cam = indice.x
        y_cam = indice.y
        x_3d = self.x_min_3d + x_cam * (self.x_max_3d - self.x_min_3d)
        # En la imagen Y aumenta hacia abajo; en la escena Z aumenta hacia arriba.
        z_3d = self.z_max_3d - y_cam * (self.z_max_3d - self.z_min_3d)

        target = (x_3d, z_3d)
        smoothing = min(0.9, max(0.12, self.cursor_smoothing * self.speed))
        if self._filtered_target is None:
            self._filtered_target = target
        else:
            self._filtered_target = self._smooth_cursor_position(
                self._filtered_target,
                target,
                smoothing=smoothing,
                dead_zone=self.cursor_dead_zone,
            )

        distancia = math.hypot(pulgar.x - indice.x, pulgar.y - indice.y)
        agarre = self._update_grab_state(distancia)
        self.event_mano.emit(*self._filtered_target, agarre)

            