
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow

from AppCore.Config import Configuration
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        TransmissionProtocol)
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Observation.TransmissionReceiver import TransmissionReceiver


class Window(QMainWindow, TransmissionReceiver):
    def __init__(self, configuration: Configuration, 
                 observation_tower: ObservationTower):
        """Initializer."""
        super().__init__()
        self.configuration = configuration
        
        # self.setWindowIcon(QtGui.QIcon('./resources/logo.png'))
        self.setGeometry(0, 0, 1200, 800)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self._load_window()

        observation_tower.subscribe(self, ConfigurationUpdatedEvent)

    def _load_window(self):
        self.setWindowTitle(self.configuration.app_display_name)

    def handle_observation_tower_event(self, event: TransmissionProtocol):
        self._load_window()