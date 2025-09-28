from PyQt5.QtWidgets import QWidget

from AppUI.AppDependenciesProviding import AppDependenciesProviding
from R4UI import TabWidget
from .SettingsViewController import SettingsViewController
from .DraftListSettingsViewController import DraftListSettingsViewController
class AppSettingsViewController(QWidget):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesProviding):
        super().__init__()
        self._app_dependencies_provider = app_dependencies_provider
        
        self._setup_view()
        
    def _setup_view(self):
        TabWidget([
            (SettingsViewController(self._app_dependencies_provider), "Image Deployer"),
            # (DraftListSettingsViewController(self._app_dependencies_provider), "Draft List Settings")
        ]).set_layout_to_widget(self)