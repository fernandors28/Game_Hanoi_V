import cv2
class Base:
    def __init(self, frame_wifth=640, frame_height=480):
        self.width = frame_wifth
        self.height = frame_height
        self.POSTE_BASE = {
            "A":{"x": 160, "y_min":300, "y_max":400},
            "B":{"x": 340, "y_min":300, "y_max":400},
            "C":{"x": 480 , "y_min":300, "y_max":400}
        }
        self.base_rect = (100, 400, 540, 420)
    def draw(self, frame):
        bx_1,by_2,bx_3,by_4 = self.base_rect
        cv2.rectangle(frame, (bx_1,by_2),(bx_3, by_4),(70,70,70),-1)
        cv2.rectangle(frame, (bx_1,by_2),(bx_3, by_4),(200,200,200),2)

        for name, poste in self.POSTE_BASE.items():
            x = poste["x"]
            y_max = poste["y_max"]
            y_min = poste["y_min"]
            cv2.line(frame,(x, y_max),(x,y_min),(100,100,100),10)
            cv2.putText(frame,f"poste {name}",(x-45, by_2 + 30),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)
        return frame
