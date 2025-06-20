
from typing import Optional

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QCloseEvent, QKeyEvent, QResizeEvent
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow

from AppCore.Observation.Events import ConfigurationUpdatedEvent
from AppCore.Observation.TransmissionReceiverProtocol import (
    TransmissionProtocol, TransmissionReceiverProtocol)

from .AppDependenciesProviding import AppDependenciesProviding
from .Observation.Events import KeyboardEvent


class Window(QMainWindow, TransmissionReceiverProtocol):
    def __init__(self,
                 app_dependencies: AppDependenciesProviding):
        """Initializer."""
        super().__init__()
        self.configuration_manager = app_dependencies.configuration_manager
        self.asset_provider = app_dependencies.asset_provider
        self.observation_tower = app_dependencies.observation_tower

        self._load_window()
        self._load_window_size()
        
        app_dependencies.menu_action_coordinator.setParent(self)
        app_dependencies.menu_action_coordinator.setNativeMenuBar(False) # can only be called after set parent
        self.setMenuBar(app_dependencies.menu_action_coordinator)
        
        self.observation_tower.subscribe(self, ConfigurationUpdatedEvent)

        self._save_async_timer = QTimer()
        self._save_async_timer.setSingleShot(True)
        self._save_async_timer.timeout.connect(self.save)
        self.debounce_time = 500
        
        self._window_size = None

    def _load_window(self):
        self.setWindowTitle(self.configuration_manager.configuration.app_display_name)
        # https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/#setting-an-application-icon
        # self.setWindowIcon(QIcon(self.asset_provider.image.logo_path))

    def _load_window_size(self):
        width, height = 400+900, 900
        if self.configuration_manager.configuration.window_size is not None:
            width = self.configuration_manager.configuration.window_size[0]
            height = self.configuration_manager.configuration.window_size[1]
        self.setGeometry(0, 0, width, height)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == ConfigurationUpdatedEvent:
            self._load_window()

            if event.configuration.window_size is None:
                self._load_window_size()
        
        
    def keyPressEvent(self, a0: Optional[QKeyEvent]):
        if a0 is not None:
            self.observation_tower.notify(KeyboardEvent(KeyboardEvent.Action.PRESSED, a0))
        
    def keyReleaseEvent(self, a0: Optional[QKeyEvent]):
        if a0 is not None:
            self.observation_tower.notify(KeyboardEvent(KeyboardEvent.Action.RELEASED, a0))

    def closeEvent(self, a0: Optional[QCloseEvent]):
        print('closing')
        # https://stackoverflow.com/a/70081754
        for window in QApplication.topLevelWidgets():
            window.close()

    def save(self):
        if self._window_size is not None:
            new_config = self.configuration_manager.mutable_configuration()
            new_config.set_window_size((self._window_size[0], self._window_size[1]))
            self.configuration_manager.save_configuration(new_config)

    def resizeEvent(self, a0: Optional[QResizeEvent]):
        # must use event value here to get size
        if a0 is not None:
            self._window_size = (a0.size().width(), a0.size().height())
            self._save_async_timer.start(self.debounce_time)
            super(Window, self).resizeEvent(a0)