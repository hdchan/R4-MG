
import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow

from AppCore.Config import ConfigurationProvider
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        TransmissionProtocol)
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Observation.TransmissionReceiver import TransmissionReceiver

basedir = os.path.dirname(__file__)
class Window(QMainWindow, TransmissionReceiver):
    def __init__(self, 
                 configuration_provider: ConfigurationProvider, 
                 observation_tower: ObservationTower):
        """Initializer."""
        super().__init__()
        self.configuration_provider = configuration_provider
        
        self.setGeometry(0, 0, 1200+150, 800)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self._load_window()

        observation_tower.subscribe(self, ConfigurationUpdatedEvent)

    def _load_window(self):
        self.setWindowTitle(self.configuration_provider.configuration.app_display_name)
        # https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/#setting-an-application-icon
        self.setWindowIcon(QIcon(os.path.join(basedir,'resources/logo.png')))

    def handle_observation_tower_event(self, event: TransmissionProtocol):
        self._load_window()