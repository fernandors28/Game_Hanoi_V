import cv2
import numpy as np


class CameraStream:
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self.cap = None

    def start(self) -> None:
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise Exception("No se pudo abrir la camara con ID")

    def get_frame(self) -> tuple[bool, np.ndarray | None]:
        if self.cap is None:
            return False, None

        ret, frame = self.cap.read()
        if ret and frame is not None:
            frame = cv2.flip(frame, 1)
        return ret, frame

    def release(self) -> None:
        if self.cap is not None:
            self.cap.release()
