from enum import Enum

from PySide6.QtGui import QKeyEvent

from AppCore.Observation.TransmissionProtocol import TransmissionProtocol


class KeyboardEvent(TransmissionProtocol):
    
    class Action(int, Enum):
        PRESSED = 1
        RELEASED = 2
    
    def __init__(self, 
                 action: Action, 
                 event: QKeyEvent):
        self.action = action
        self.event = event