import cv2
class CameraStream:
    def __init__(self,camera_id=0):
        self.camera_id = camera_id
        self.cap = None
    def start(self):
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise Exception(f"No se pudo abrir la camara con ID")
    def get_frame(self):
        if self.cap is None:
            return False, None
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
        return ret, frame
    def release(self):
        if self.cap is not None:
            self.cap.release()
