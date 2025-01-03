import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import QPropertyAnimation, QRect, QPoint, pyqtProperty, QSize, Qt, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient
import math


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        # self.last_location = (100, 100)
        self.location = (100, 100)
        self.previous_location = (200, 200)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawEllipse(self.location[0] - 100, self.location[1] - 100, 200, 200)
        theta = math.atan2((self.location[1] - self.previous_location[1]), (self.location[0] - self.previous_location[0]))
        x, y = 100 * math.cos(theta), 100 * math.sin(theta)
        painter.drawEllipse(self.location[0] - x - 50, self.location[1] - y - 50, 100, 100)
        painter.end()
        
    def mouseMoveEvent(self, e):
        self.previous_location = self.location
        self.location = (e.x(), e.y())
        self.update()
        
    
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    # widget.setFixedSize(QSize(128, 128))
    widget.show()
    sys.exit(app.exec_())