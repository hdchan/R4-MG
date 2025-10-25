
from typing import List, Optional

from PySide6.QtCore import  Qt
from PySide6.QtWidgets import (QSplitter)

from .RWidget import RWidget

class Splitter(QSplitter):
    def __init__(self, 
                 orientation: Qt.Orientation, 
                 widgets: List[RWidget], 
                 weights: List[Optional[int]] = []):
        super().__init__()
        self.setOrientation(orientation)
        self._widgets: List[RWidget] = []
        self.add_widgets(widgets, weights)
    
    def add_widget(self, widget: RWidget):
        self.add_widgets([widget], [])

    def add_widgets(self, 
                    widgets: List[RWidget], 
                    weights: List[Optional[int]]):
        for i, w in enumerate(widgets):
            self._widgets.append(w)
            self.addWidget(w)
            if i < len(weights):
                weight = weights[i]
                if weight is not None:
                    self.setStretchFactor(i, weight)
            
class HorizontalSplitter(Splitter):
    def __init__(self,
                 widgets: List[RWidget] = [], 
                 weights: List[Optional[int]] = []):
        super().__init__(Qt.Orientation.Horizontal, widgets, weights)
        
class VerticalSplitter(Splitter):
    def __init__(self,
                 widgets: List[RWidget] = [],
                 weights: List[Optional[int]] = []):
        super().__init__(Qt.Orientation.Vertical, widgets, weights)