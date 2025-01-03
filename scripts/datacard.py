import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import QPropertyAnimation, QRect, QPoint, pyqtProperty, QSize, Qt, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient
import math
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self._angle = 0
        self.rotatione_animation = QPropertyAnimation(self, b"angle")
        self.rotatione_animation.setDuration(5000)  # Animation duration in milliseconds
        self.rotatione_animation.setStartValue(0)
        self.rotatione_animation.setEndValue(360)
        self.rotatione_animation.setLoopCount(-1)  # Loop indefinitely
        # self.rotatione_animation.start()
        
        start = 0.4
        self._shine = 0.4
        self._shine_width = 0.1
        self.shine_animation = QPropertyAnimation(self, b"shine")
        # self.shine_animation.setEasingCurve(QEasingCurve.OutInCubic)
        self.shine_animation.setDuration(5000)  # Animation duration in milliseconds
        self.shine_animation.setStartValue(start)
        self.shine_animation.setKeyValueAt(0.5, 0.9)
        self.shine_animation.setEndValue(start)
        self.shine_animation.setLoopCount(-1)
        self.shine_animation.start()

    def paintEvent(self, event):
        
        circle_painter = QPainter(self)
        circle_painter.setRenderHint(QPainter.Antialiasing)

        window_w = circle_painter.device().width()
        window_h = circle_painter.device().height()
        disc_w = window_w * 0.8
        disc_h = window_h * 0.8
        disc_orig_x, disc_orig_y = (window_w - disc_w)/2, (window_h - disc_h)/2
        
        
        
        min_d = min(disc_w, disc_h)
        t = min_d * 0.005
        
        pen = QPen(QColor('#000'), t, cap=Qt.FlatCap)
        circle_painter.setPen(pen)
        
        gradient = QLinearGradient(disc_orig_x, disc_orig_y, disc_w, disc_h)
        gradient.setColorAt(0.00, QColor('#AE8625'))
        gradient.setColorAt(0.4, QColor('#F7EF8A'))
        gradient.setColorAt(0.8, QColor('#D2AC47'))
        gradient.setColorAt(0.9, QColor('#EDC967'))
        
        # gradient.setColorAt(0.25, QColor('red'))
        # gradient.setColorAt(0.75, QColor('green'))
        
        # gradient.setColorAt(0.1, QColor('#DFBD69'))
        # gradient.setColorAt(self._shine, QColor('#F7EF8A'))
        # gradient.setColorAt(0.9, QColor('#926F34'))
        
        
        # gradient.setColorAt(0.1, QColor('#F9F295'))
        # gradient.setColorAt(0.3, QColor('#E0AA3E'))
        # gradient.setColorAt(0.75, QColor('#FAF398'))
        # gradient.setColorAt(0.95, QColor('B88A44'))
        circle_painter.setBrush(QBrush(gradient))

        def get_size(m):
            return min_d * m - t * 2
        
        def local_origin(size):
            return ((disc_w - size)/2, (disc_h - size) / 2)
        
        def arc_line_pos(size, t):
            return (disc_w / 2) + (size / 2 * math.cos(t)), (disc_h / 2) + (size / 2 * math.sin(t))

        disc_multipliers = [.95, .90, .70, .50, .30]
        for m in disc_multipliers:
            circle_size = get_size(m)
            circle_origin_x, circle_origin_y = local_origin(circle_size)
            circle_painter.drawEllipse(circle_origin_x + disc_orig_x, circle_origin_y + disc_orig_y, circle_size, circle_size)

        arc_painter = QPainter(self)
        arc_painter.setPen(pen)
        arc_painter.setRenderHint(QPainter.Antialiasing)
        for i in range(0, 60):
            if i > 35 and i < 55:
                continue
            # upper
            theta = -i * math.pi/30 + (self._angle * math.pi / 180)
            if i == 35 or i == 55:
                arc_line_top_pos = get_size(0.9)
            else:
                arc_line_top_pos = get_size(0.86)
            x_1, y_1 = arc_line_pos(arc_line_top_pos, theta)
            
            # lower
            arc_line_bot_pos = get_size(0.8)
            x_0, y_0 = arc_line_pos(arc_line_bot_pos, theta)
            
            arc_painter.drawLine(x_0 + disc_orig_x, y_0 + disc_orig_y, x_1 + disc_orig_x, y_1 + disc_orig_y)
        
        arc_size = get_size(0.8)
        arc_origin_x, arc_origin_y = local_origin(arc_size)
        arc_painter.drawArc(arc_origin_x + disc_orig_x, arc_origin_y + disc_orig_y, arc_size, arc_size, (-30 - self._angle) * 16 - t * 1, (240) * 16 + (t * 2))


        # Lines
        painter_guide = QPainter(self)
        
        painter_guide.setPen(QPen(QColor('red'), 1, cap=Qt.FlatCap))
        
        painter_guide.drawLine(window_w/2, 0, window_w/2, window_h)
        painter_guide.drawLine(0, window_h/2, window_w, window_h/2)
        min_od = min(window_h, window_w)
        painter_guide.drawRect((window_w-min_od)/2, (window_h-min_od)/2, min_od, min_od)

        arc_size = get_size(1)
        arc_origin_x, arc_origin_y = local_origin(arc_size)
        painter_guide.drawRect(arc_origin_x + disc_orig_x, arc_origin_y + disc_orig_y,  min_d, min_d)
        
        theta = -45 * math.pi / 60
        x, y = arc_line_pos(get_size(0.95), theta)
        painter_guide.drawLine(arc_origin_x + disc_orig_x, y + disc_orig_y, x + disc_orig_x, y + disc_orig_y)
        
        theta = -47 * math.pi / 60
        x, y = arc_line_pos(get_size(0.95), theta)
        painter_guide.drawLine(arc_origin_x + disc_orig_x, y + disc_orig_y, x + disc_orig_x, y + disc_orig_y)

    @pyqtProperty(int)
    def angle(self):
        return self._angle
    
    @angle.setter
    def angle(self, value):
        self._angle = value
        self.update()
        
    @pyqtProperty(float)
    def shine(self):
        return self._shine
    
    @shine.setter
    def shine(self, value):
        self._shine = value
        self.update()
        
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    # widget.setFixedSize(QSize(128, 128))
    widget.show()
    sys.exit(app.exec_())