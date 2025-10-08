from typing import List, Tuple

from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from AppUI.UIComponents.Base.SettingsContainerChildProtocol import *
from R4UI import (HorizontalBoxLayout, PushButton, R4UITabWidget, R4UIWidget,
                  VerticalBoxLayout)

from .DraftListSettingsViewController import DraftListSettingsViewController
from .ImageDeploymentSettingsViewController import ImageDeploymentSettingsViewController
from .ToggleSettingsViewController import ToggleSettingsViewController

class AppSettingsViewController(R4UIWidget):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        self._app_dependencies_provider = app_dependencies_provider
        self._app_ui_configuration_manager = app_dependencies_provider.app_ui_configuration_manager

        self._setup_view()

    def _setup_view(self):
        self.setWindowTitle("Settings")

        self._children: List[Tuple[SettingsContainerChildProtocol, str]] = [
            (ImageDeploymentSettingsViewController(self._app_dependencies_provider), "Image Deployer"),
            (DraftListSettingsViewController(self._app_dependencies_provider), "Draft List"),
            (ToggleSettingsViewController(self._app_dependencies_provider), "Toggles")
        ]
        
        VerticalBoxLayout([
            R4UITabWidget(self._children),
            HorizontalBoxLayout([
                PushButton("Apply", self._apply),
                PushButton("Save && Close", self._save_and_close)
            ])
        ]).set_layout_to_widget(self)
        
    def _apply(self):
        current_mutable_configuration_instance = self._app_ui_configuration_manager.mutable_configuration()
        for c in self._children:
            current_mutable_configuration_instance = c[0].will_apply_settings(current_mutable_configuration_instance)
        self._app_ui_configuration_manager.save_configuration(current_mutable_configuration_instance)
    
    def _save_and_close(self):
        self._apply()
        self.close()