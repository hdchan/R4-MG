from typing import List

from PyQt5.QtWidgets import QWidget

from AppUI.AppDependenciesProviding import AppDependenciesProviding
from AppUI.UIComponents import SettingsContainerChildProtocol
from PyQtUI import HorizontalBoxLayout, PushButton, VerticalBoxLayout

from .DraftListSettingsViewController import DraftListSettingsViewController


class SettingsContainerViewController(QWidget):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesProviding):
        super().__init__()
        self._app_ui_configuration_manager = app_dependencies_provider.app_ui_configuration_manager
        self._mutable_configuration_instance = app_dependencies_provider.app_ui_configuration_manager.mutable_configuration()
        self._children: List[SettingsContainerChildProtocol] = []
        
        self._draft_list_settings = DraftListSettingsViewController(app_dependencies_provider, self._mutable_configuration_instance)
        self._children.append(self._draft_list_settings)
        
        VerticalBoxLayout([
            self._draft_list_settings,
            HorizontalBoxLayout([
                PushButton("Apply", self._apply),
                PushButton("Save && Close", self._save_and_close)
            ])
        ]).set_to_layout(self)
        
    def _apply(self):
        current_mutable_configuration_instance = self._app_ui_configuration_manager.mutable_configuration()
        for c in self._children:
            new = c.will_apply_settings(current_mutable_configuration_instance)
            if new is not None:
                current_mutable_configuration_instance = new
        
        self._app_ui_configuration_manager.save_configuration(current_mutable_configuration_instance)
    
    def _save_and_close(self):
        self._apply()
        self.close()