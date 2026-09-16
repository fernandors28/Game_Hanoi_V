import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PyQt6.QtCore  import QObject, QTimer,  pyqtSignal
import math
import cv2
import os

class ControlGesto(QObject):
    event_mano = pyqtSignal(str, int, int)
    def init__(self,x_min_3d,x_max_3d, z_min_3d, z_max_3d):
        self.x_min_3d = x_min_3d
        self.x_max_3d = x_max_3d
        self.z_min_3d = z_min_3d
        self.z_max_3d = z_max_3d
           
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
        self.timer =QTimer()
        self.timer.timeout.connect(self.procesar_frame)
  
    def init(self, fps=30):
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
        if resultado:
            mano = resultado.hand_landmarks[0]
            pulgar =mano[4]
            indice = mano[8]

            x_cam = indice.x
            y_cam = indice.y
            x_3d = self.x_min_3d + x_cam *(self.x_max_3d - self.x_min_3d)
            z_3d = self.z_min_3d +y_cam * (self.z_max_3d - self.z_min_3d) 

            distancia = math.hypot(pulgar.x-indice.x, pulgar.y . indice.y)
            agarre = distancia < 0.08
            self.event_mano.emit(x_3d,z_3d,agarre)

            