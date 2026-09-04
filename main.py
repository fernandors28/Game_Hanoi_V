import sys
from PyQt6.QtWidgets import  QApplication
from window import Window_Game

      
    
if __name__ == "__main__": 
    app = QApplication(sys.argv)     
    game =Window_Game()
    game.show()
    sys.exit(app.exec())