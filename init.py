from UI.Main import Window_Game
import tkinter as tk
import cv2
from src.camera import CameraStream
from UI.Base_Game import Base


def Main():
    cam = CameraStream(0)
    cam.start()

    renderer = Base()
    print("iniciamos la torre de Hanoi. Presiona 'q' para salir")
    while True:
        ret, frame = cam.get_frame()
        if not ret:
            print("error al capturar")
            break
        frame = renderer.draw(frame)
        cv2.imshow("Hanoi", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    Window_Game()


   