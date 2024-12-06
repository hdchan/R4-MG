
import os
from typing import Optional

from PyQt5.QtGui import QCloseEvent, QKeyEvent, QResizeEvent
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QMenuBar, QMenu

from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        TransmissionProtocol)
from AppCore.Observation.TransmissionReceiverProtocol import \
    TransmissionReceiverProtocol

from .AppDependencyProviding import AppDependencyProviding
from .Observation.Events import KeyboardEvent

basedir = os.path.dirname(__file__)
class Window(QMainWindow, TransmissionReceiverProtocol):
    def __init__(self,
                 app_dependencies: AppDependencyProviding):
        """Initializer."""
        super().__init__()
        self.configuration_manager = app_dependencies.configuration_manager
        self.asset_provider = app_dependencies.asset_provider
        self.observation_tower = app_dependencies.observation_tower
        
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

        app_dependencies.menu_action_coordinator.setParent(self)
        app_dependencies.menu_action_coordinator.setNativeMenuBar(False) # can only be called after set parent
        self.setMenuBar(app_dependencies.menu_action_coordinator)
        
        self.observation_tower.subscribe(self, ConfigurationUpdatedEvent)

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
        # TOOD: save and close all windows
    
    def resizeEvent(self, a0: Optional[QResizeEvent]):
        # must use event value here to get size
        if a0 is not None:
            size = a0.size()
            self.configuration_manager.set_window_size((size.width(), size.height())).save_async()
            super(Window, self).resizeEvent(a0)