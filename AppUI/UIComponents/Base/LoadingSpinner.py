from pyqtwaitingspinner import WaitingSpinner, SpinnerParameters, SpinDirection
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget

class LoadingSpinner(WaitingSpinner):
    def __init__(self, parent: QWidget):
        # super().__init__(
        #     parent,
        #     roundness=100.0,
        #     # opacity=17.49,
        #     fade=49.83,
        #     radius=8,
        #     lines=44,
        #     line_length=10,
        #     line_width=6,
        #     speed=3.0999999999999996,
        #     color=QColor(0, 0, 0)
        # )
        params = SpinnerParameters(
                roundness=100.0,
                trail_fade_percentage=67.0,
                number_of_lines=8,
                line_length=40,
                line_width=40,
                inner_radius=32,
                revolutions_per_second=1.0,
                color=QColor(0, 170, 0),
                minimum_trail_opacity=1.0,
                spin_direction=SpinDirection.COUNTERCLOCKWISE,
                center_on_parent=True,
                disable_parent_when_spinning=False,
            )
        super().__init__(parent, spinner_parameters=params)

