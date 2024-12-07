
import os
from typing import Optional
from PyQt5.QtCore import QTimer

from PyQt5.QtGui import QKeyEvent, QCloseEvent
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow

from AppCore.Config import ConfigurationProviderProtocol, ConfigurationManager
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        TransmissionProtocol)
from AppCore.Observation.ObservationTower import ObservationTower
from AppCore.Observation.TransmissionReceiverProtocol import TransmissionReceiverProtocol

from .Assets import AssetProvider
from .Observation.Events import KeyboardEvent

basedir = os.path.dirname(__file__)
class Window(QMainWindow, TransmissionReceiverProtocol):
    def __init__(self,
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower, 
                 asset_provider: AssetProvider):
        """Initializer."""
        super().__init__()
        self.configuration_manager = configuration_manager
        self.asset_provider = asset_provider
        self.observation_tower = observation_tower
        
        
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._save_window_position)
        self.debounce_time = 500
        
        width, height = 400+900, 900
        if (self.configuration_manager.configuration.window_size[0] is not None and
            self.configuration_manager.configuration.window_size[1] is not None):
            
            width = self.configuration_manager.configuration.window_size[0]
            height = self.configuration_manager.configuration.window_size[1]
        
        self.setGeometry(0, 0, width, height)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self._load_window()
        
        observation_tower.subscribe(self, ConfigurationUpdatedEvent)

    def _load_window(self):
        self.setWindowTitle(self.configuration_manager.configuration.app_display_name)
        # https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/#setting-an-application-icon
        # self.setWindowIcon(QIcon(self.asset_provider.image.logo_path))

    def handle_observation_tower_event(self, event: TransmissionProtocol):
        self._load_window()
        
    def keyPressEvent(self, a0: Optional[QKeyEvent]):
        if a0 is not None:
            self.observation_tower.notify(KeyboardEvent(KeyboardEvent.Action.PRESSED, a0))
        
    def keyReleaseEvent(self, a0: Optional[QKeyEvent]):
        if a0 is not None:
            self.observation_tower.notify(KeyboardEvent(KeyboardEvent.Action.RELEASED, a0))

    def closeEvent(self, a0: Optional[QCloseEvent]):
        print('closing')
    
    def _save_window_position(self):
        
        size = self.frameGeometry()
        print(f'saving {size}')
        self.configuration_manager.set_window_size((size.width(), size.height())).save()
        
    def resizeEvent(self, event):
        self.timer.start(self.debounce_time)
        
        super(Window, self).resizeEvent(event)