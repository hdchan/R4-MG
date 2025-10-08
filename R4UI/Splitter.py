
from typing import List

from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QSplitter)

from .R4UIWidget import R4UIWidget

class Splitter(QSplitter):
    def __init__(self, 
                 orientation: Qt.Orientation, 
                 widgets: List[R4UIWidget]):
        super().__init__()
        self.setOrientation(orientation)
        self._widgets: List[R4UIWidget] = []
        self.add_widgets(widgets)
        
    def add_widgets(self, widgets: List[R4UIWidget]):
        for w in widgets:
            self._widgets.append(w)
            self.addWidget(w)
            
class HorizontalSplitter(Splitter):
    def __init__(self,
                 widgets: List[R4UIWidget]):
        super().__init__(Qt.Orientation.Horizontal, widgets)
        
class VerticalSplitter(Splitter):
    def __init__(self,
                 widgets: List[R4UIWidget]):
        super().__init__(Qt.Orientation.Vertical, widgets)