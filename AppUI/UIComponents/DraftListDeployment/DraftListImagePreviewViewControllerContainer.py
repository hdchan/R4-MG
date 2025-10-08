from PyQt5.QtWidgets import QWidget

from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from R4UI import VerticalBoxLayout


class DraftListImagePreviewViewControllerContainer(QWidget):
    def __init__(self, app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        self._data_source_draft_list = app_dependencies_provider.data_source_draft_list
        self._external_app_dependencies_provider = app_dependencies_provider.external_app_dependencies_provider
        self._observation_tower = app_dependencies_provider.observation_tower
        
        VerticalBoxLayout([
            self._external_app_dependencies_provider.provide_draft_list_image_preview_widget(self._data_source_draft_list)
        ]).set_layout_to_widget(self)