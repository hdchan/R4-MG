import sys
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 2))

        # Draw the original line
        painter.drawLine(10, 10, 100, 100)

        # Translate the coordinate system
        painter.translate(500, 500)

        # Draw the translated line (same coordinates as the first line)
        painter.drawLine(10, 10, 100, 100)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec_())