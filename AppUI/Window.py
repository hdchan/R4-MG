
import os
from typing import Optional

from PyQt5.QtGui import QIcon, QKeyEvent
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow

from AppCore.Config import ConfigurationProvider
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        TransmissionProtocol)
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Observation.TransmissionReceiver import TransmissionReceiver

from .Assets import AssetProvider
from .Observation.Events import KeyboardEvent

basedir = os.path.dirname(__file__)
class Window(QMainWindow, TransmissionReceiver):
    def __init__(self, 
                 configuration_provider: ConfigurationProvider, 
                 observation_tower: ObservationTower, 
                 asset_provider: AssetProvider):
        """Initializer."""
        super().__init__()
        self.configuration_provider = configuration_provider
        self.asset_provider = asset_provider
        self.observation_tower = observation_tower
        
        self.setGeometry(0, 0, 400+900, 900)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self._load_window()
        
        observation_tower.subscribe(self, ConfigurationUpdatedEvent)

    def _load_window(self):
        self.setWindowTitle(self.configuration_provider.configuration.app_display_name)
        # https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/#setting-an-application-icon
        self.setWindowIcon(QIcon(self.asset_provider.image.logo_path))

    def handle_observation_tower_event(self, event: TransmissionProtocol):
        self._load_window()
        
    def keyPressEvent(self, a0: Optional[QKeyEvent]):
        if a0 is not None:
            self.observation_tower.notify(KeyboardEvent(KeyboardEvent.Action.PRESSED, a0))
        
    def keyReleaseEvent(self, a0: Optional[QKeyEvent]):
        if a0 is not None:
            self.observation_tower.notify(KeyboardEvent(KeyboardEvent.Action.RELEASED, a0))