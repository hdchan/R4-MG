import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import QPropertyAnimation, QRect, QPoint, pyqtProperty, QSize, Qt
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient
import math
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        # self.angle = 0
        # self.angle2= 0
        # self.animation = QPropertyAnimation(self, b"angle")
        # self.animation.setDuration(750)  # Animation duration in milliseconds
        # self.animation.setStartValue(0)
        # self.animation.setEndValue(360)
        # self.animation.setLoopCount(-1)  # Loop indefinitely
        # self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        
        w = painter.device().width()
        h = painter.device().height()
        min_d = min(painter.device().width(), painter.device().height())
        t = min_d * 0.005
        pen = QPen(QColor('#000'), t, cap=Qt.FlatCap)
        painter.setPen(pen)
        multipliers = [.99, .90, .70, .50, .30]

        gradient = QLinearGradient(0, 0, w, h)
        gradient.setColorAt(0.00, QColor('#AE8625'))
        gradient.setColorAt(0.45, QColor('#F7EF8A'))
        gradient.setColorAt(0.85, QColor('#D2AC47'))
        gradient.setColorAt(0.95, QColor('#EDC967'))
        painter.setBrush(QBrush(gradient))


        for m in multipliers:
            size = min_d * m - t * 2
            painter.drawEllipse((w - size) / 2, (h - size) / 2, size, size)
            # painter.rotate(i * 20 *)

        line_painter = QPainter(self)
        line_painter.setPen(pen)
        line_painter.setRenderHint(QPainter.Antialiasing)
        for i in range(0, 60):
            if i > 35 and i < 55:
                continue
            theta = -i * math.pi/30
            if i == 35 or i == 55:
                size = min_d * 0.90 - t * 2
                new_x, new_y = (w/2) + (size / 2 * math.cos(theta)), (h/2) + (size / 2 * math.sin(theta)) 
            else:
                size = min_d * 0.86 - t * 2
                new_x, new_y = (w/2) + (size / 2 * math.cos(theta)), (h/2) + (size / 2 * math.sin(theta)) 
            
            size2 = min_d * 0.8 - t * 2
            new_x_2, new_y_2 = (w/2) + (size2 / 2 * math.cos(theta)), (h/2) + (size2 / 2 * math.sin(theta)) 
            
            line_painter.drawLine(new_x_2, new_y_2, new_x, new_y)
        
        arc_painter = QPainter(self)
        arc_painter.setPen(pen)
        arc_painter.setRenderHint(QPainter.Antialiasing)
        size = min_d * 0.8 - t * 2
        arc_painter.drawArc((w-size)/2, (h-size)/2, size, size, -30 * 16 - t * 1, (180+60) * 16 + (t * 2))
        
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.setFixedSize(QSize(128, 128))
    widget.show()
    sys.exit(app.exec_())