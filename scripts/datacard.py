import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import QPropertyAnimation, QRect, QPoint, pyqtProperty, QSize, Qt
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient

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
        thickness = w * 0.01
        painter.setPen(QPen(QColor('#FFFFFF'), thickness, cap=Qt.FlatCap))
        multipliers = [.99, .90, .70, .50, .30]

        gradient = QLinearGradient(0, 0, w, h)
        gradient.setColorAt(0.00, QColor('#AE8625'))
        gradient.setColorAt(0.45, QColor('#F7EF8A'))
        gradient.setColorAt(0.85, QColor('#D2AC47'))
        gradient.setColorAt(0.95, QColor('#EDC967'))
        painter.setBrush(QBrush(gradient))

        t = thickness
        min_d = min(painter.device().width(), painter.device().height())

        for m in multipliers:
            
            
            size = min_d * m - t * 2
            painter.drawEllipse((w - size) / 2 + t, (h - size) / 2 + t, size, size)
            # painter.rotate(i * 20 *)

        line_painter = QPainter(self)
        line_painter.setPen(QPen(QColor('#000000'), 1, cap=Qt.FlatCap))
        line_painter.drawLine(w/2 + t, h/2 + t, 0, h/2)

        line_painter.translate(self.width() / 2, self.height() / 2)
        line_painter.rotate(45)
        line_painter.translate(-self.width() / 2, -self.height() / 2)
        line_painter.drawLine(w/2 + t, h/2 + t, 0, h/2)

        line_painter.translate(self.width() / 2, self.height() / 2)
        line_painter.rotate(45)
        line_painter.translate(-self.width() / 2, -self.height() / 2)
        line_painter.drawLine(w/2 + t, h/2 + t, 0, h/2)

        line_painter.translate(self.width() / 2, self.height() / 2)
        line_painter.rotate(45)
        line_painter.translate(-self.width() / 2, -self.height() / 2)
        line_painter.drawLine(w/2 + t, h/2 + t, 0, h/2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    # widget.setFixedSize(QSize(100, 100))
    widget.show()
    sys.exit(app.exec_())