
from typing import Optional

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QCloseEvent, QKeyEvent, QResizeEvent
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QWidget

from AppCore.Observation.TransmissionReceiverProtocol import \
    TransmissionReceiverProtocol
from AppUI.AppDependenciesProviding import AppDependenciesProviding
from AppUI.Observation.Events import KeyboardEvent
from AppUI.Models import WindowDimensions

class AppWindow(QMainWindow, TransmissionReceiverProtocol):
    
    def __init__(self,
                 app_dependencies_provider: AppDependenciesProviding, 
                 central_widget: QWidget, 
                 window_config_identifier: str,
                 default_width: int, 
                 default_height: int):
        super().__init__()
        self._app_ui_configuration_manager = app_dependencies_provider.app_ui_configuration_manager
        self._observation_tower = app_dependencies_provider.observation_tower
        self._router = app_dependencies_provider.router
        self._window_config_identifier = window_config_identifier
        self._default_width = default_width
        self._default_height = default_height
        self._load_window()
        self._load_window_size()

        self._save_async_timer = QTimer()
        self._save_async_timer.setSingleShot(True)
        self._save_async_timer.timeout.connect(self.save)
        self.debounce_time = 500
        
        self._window_size = None
        
        self.setCentralWidget(central_widget)

    def _load_window(self):
        self.setWindowTitle(self._app_ui_configuration_manager.configuration.core_configuration.app_display_name)

    def _load_window_size(self):
        width, height = self._default_width, self._default_height
        config_result = self._app_ui_configuration_manager.configuration.window_dimensions.window_dimensions(self._window_config_identifier)
        self._app_ui_configuration_manager.configuration.window_dimensions
        if config_result is not None:
            width = config_result[0]
            height = config_result[1]
        self.setGeometry(0, 0, width, height)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        
        
    def keyPressEvent(self, a0: Optional[QKeyEvent]):
        if a0 is not None:
            self._observation_tower.notify(KeyboardEvent(KeyboardEvent.Action.PRESSED, a0))
        
    def keyReleaseEvent(self, a0: Optional[QKeyEvent]):
        if a0 is not None:
            self._observation_tower.notify(KeyboardEvent(KeyboardEvent.Action.RELEASED, a0))

    def closeEvent(self, a0: Optional[QCloseEvent]):
        print('closing')
        # https://stackoverflow.com/a/70081754
        # for window in QApplication.topLevelWidgets():
        #     window.close()
        # self._router.close_all_child_views()

    def save(self):
        if self._window_size is not None:
            new_config = self._app_ui_configuration_manager.mutable_configuration()
            # H/W parameters might be reversed
            new_window_dimensions = new_config.window_dimensions
            new_window_dimensions.set_window_dimensions(self._window_config_identifier, self._window_size[0], self._window_size[1])
            new_config.set_window_dimensions(new_window_dimensions)
            self._app_ui_configuration_manager.save_configuration(new_config)

    def resizeEvent(self, a0: Optional[QResizeEvent]):
        # must use event value here to get size
        if a0 is not None:
            self._window_size = (a0.size().width(), a0.size().height())
            self._save_async_timer.start(self.debounce_time)
            super(AppWindow, self).resizeEvent(a0)