
from PyQt5.QtWidgets import QWidget

from AppCore.Models import LocalAssetResource, LocalResourceDraftListWindow


class ScreenWidgetProviding:
    @property
    def about_view(self) -> QWidget:
        return NotImplemented
    
    @property
    def app_settings_view(self) -> QWidget:
        return NotImplemented
    
    @property
    def shortcuts_view(self) -> QWidget:
        return NotImplemented
    
    @property
    def manage_deck_list_view(self) -> QWidget:
        return NotImplemented
    
    def locally_managed_deck_preview_view(self, resource: LocalAssetResource) -> QWidget:
        return NotImplemented
    
    def draft_list_standalone_view(self, resource: LocalResourceDraftListWindow) -> QWidget:
        return NotImplemented
    
    def image_deployment_window(self) -> QWidget:
        return NotImplemented
    
    def draft_list_deployment_window(self) -> QWidget:
        return NotImplemented
    
    def draft_list_image_preview_view(self) -> QWidget:
        return NotImplemented