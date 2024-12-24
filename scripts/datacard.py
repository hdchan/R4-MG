import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import QPropertyAnimation, QRect, QPoint, pyqtProperty, QSize, Qt
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient
import math
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self._angle = 0
        self.rotatione_animation = QPropertyAnimation(self, b"angle")
        self.rotatione_animation.setDuration(500)  # Animation duration in milliseconds
        self.rotatione_animation.setStartValue(0)
        self.rotatione_animation.setEndValue(360)
        self.rotatione_animation.setLoopCount(-1)  # Loop indefinitely
        # self.rotatione_animation.start()
        
        

    def paintEvent(self, event):
        circle_painter = QPainter(self)
        circle_painter.setRenderHint(QPainter.Antialiasing)

        
        w = circle_painter.device().width()
        h = circle_painter.device().height()
        min_d = min(w, h)
        t = min_d * 0.005
        pen = QPen(QColor('#000'), t, cap=Qt.FlatCap)
        circle_painter.setPen(pen)
        
        multipliers = [.99, .90, .70, .50, .30]

        gradient = QLinearGradient(0, 0, w, h)
        gradient.setColorAt(0.00, QColor('#AE8625'))
        gradient.setColorAt(0.45, QColor('#F7EF8A'))
        gradient.setColorAt(0.85, QColor('#D2AC47'))
        gradient.setColorAt(0.95, QColor('#EDC967'))
        circle_painter.setBrush(QBrush(gradient))

        def get_size(m):
            return min_d * m - t * 2

        for m in multipliers:
            size = get_size(m)
            circle_painter.drawEllipse((w - size) / 2, (h - size) / 2, size, size)

        line_painter = QPainter(self)
        line_painter.setPen(pen)
        line_painter.setRenderHint(QPainter.Antialiasing)
        
        for i in range(0, 60):
            if i > 35 and i < 55:
                continue
            # upper
            theta = -i * math.pi/30 + (self._angle * math.pi / 180)
            if i == 35 or i == 55:
                size = get_size(0.9)
            else:
                size = get_size(0.86)
            new_x, new_y = (w/2) + (size / 2 * math.cos(theta)), (h/2) + (size / 2 * math.sin(theta)) 
            
            # lower
            size2 = get_size(0.8)
            new_x_2, new_y_2 = (w/2) + (size2 / 2 * math.cos(theta)), (h/2) + (size2 / 2 * math.sin(theta)) 
            
            line_painter.drawLine(new_x_2, new_y_2, new_x, new_y)
        
        arc_painter = QPainter(self)
        arc_painter.setPen(pen)
        arc_painter.setRenderHint(QPainter.Antialiasing)
        size = get_size(0.8)
        arc_painter.drawArc((w-size)/2, (h-size)/2, size, size, (-30 - self._angle) * 16 - t * 1, (240) * 16 + (t * 2))


    @pyqtProperty(int)
    def angle(self):
        return self._angle
    
    @angle.setter
    def angle(self, value):
        self._angle = value
        self.update()
        
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    # widget.setFixedSize(QSize(128, 128))
    widget.show()
    sys.exit(app.exec_())