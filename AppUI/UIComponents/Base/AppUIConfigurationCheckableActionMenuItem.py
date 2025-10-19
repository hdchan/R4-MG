from typing import Callable

from PyQt5.QtWidgets import QAction

from AppCore.Config.ConfigurationManager import *
from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from AppUI.Configuration.AppUIConfiguration import *

class AppUIConfigurationCheckableRActionMenuItem(QAction, TransmissionReceiverProtocol):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesInternalProviding, 
                 text: str,
                 is_checked: Callable[[AppUIConfiguration], bool],
                 triggered_fn: Callable[[MutableAppUIConfiguration, AppUIConfiguration], None]):
        super().__init__(text)
        app_dependencies_provider.observation_tower.subscribe(self, ConfigurationUpdatedEvent)
        self._app_ui_configuration_manager = app_dependencies_provider.app_ui_configuration_manager
        self._configuration_manager = app_dependencies_provider.configuration_manager
        self._is_checked = is_checked
        self._triggered_fn = triggered_fn
        self.triggered.connect(self._triggered)
        self.setCheckable(True)
        self._sync_ui()
        
    def _sync_ui(self):
        self.setChecked(self._is_checked(self._app_ui_configuration_manager.configuration))
        
    def _triggered(self):
        new_config = self._app_ui_configuration_manager.mutable_configuration()
        self._triggered_fn(new_config, self._app_ui_configuration_manager.configuration)
        self._app_ui_configuration_manager.save_configuration(new_config)
    
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == ConfigurationUpdatedEvent:
            self._sync_ui()