import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QWheelEvent, QPalette, QColor, QResizeEvent

class Stuff(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(True)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Text"))
        layout.addWidget(QLabel("Text"))
        layout.addWidget(QLabel("Text"))
        layout.addWidget(QLabel("Text"))
        self.lay = layout
        self.setLayout(layout)

        print(self.height())

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.index = 0
        # Make the main widget a reasonable size so child widgets are visible
        self.setFixedSize(400, 300)

        self.container = Stuff(self)
        # self.container.setFixedSize(200, 50)
        self.container.setStyleSheet('background-color: blue;')
        self.container.move(0, 0)

        # self.container2 = Stuff(self)
        # self.container2.setFixedSize(200, 50)
        # self.container2.setStyleSheet('background-color: red;')
        # self.container2.move(0, self.container.pos().y() + self.container.height())

        # self.container3 = Stuff(self)
        # self.container3.setFixedSize(200, 50)
        # self.container3.setStyleSheet('background-color: yellow;')
        # self.container3.move(0, 50*2)

        # self.container4 = Stuff(self)
        # self.container4.setFixedSize(200, 50)
        # self.container4.setStyleSheet('background-color: green;')
        # self.container4.move(0, 50*3)

        self.containers = [
            self.container, 
            # self.container2,
            # self.container3,
            # self.container4
        ]

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel scroll events."""
        # Get the scroll delta (angleDelta() is always provided)
        delta = event.angleDelta().y()
        self.index += 1 if delta > 0 else -1
        
        for c in self.containers:
            y_delta = delta / 8
            c.move(0, c.pos().y() - y_delta)

            # # circle back around
            # if c.pos().y() > self.height():
            #     c.move(0, 0 - c.height() - y_delta)
            # elif c.pos().y() + c.height() < 0:
            #     c.move(0, self.height() - y_delta)

        # calculate count above and below threshold 
        # rearrange accordingly
        # one cell will always be buffered and not rendered

        # Accept the event so it stops propagating to parent widgets
        event.accept() 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec_())