from pyqtspinner import WaitingSpinner
from PyQt5.QtGui import QColor
from R4UI import RWidget

class LoadingSpinner(WaitingSpinner):
    def __init__(self, parent: RWidget):
        super().__init__(
            parent,
            roundness=100.0,
            # opacity=17.49,
            fade=49.83,
            radius=8,
            lines=44,
            line_length=10,
            line_width=6,
            speed=3.0999999999999996,
            color=QColor(0, 0, 0)
        )

