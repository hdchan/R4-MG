
from AppCore.Models import LocalAssetResource, LocalResourceDraftListWindow
from R4UI import RWidget

class ScreenWidgetProviding:
    @property
    def about_view(self) -> RWidget:
        return NotImplemented
    
    @property
    def app_settings_view(self) -> RWidget:
        return NotImplemented
    
    @property
    def shortcuts_view(self) -> RWidget:
        return NotImplemented
    
    @property
    def manage_deck_list_view(self) -> RWidget:
        return NotImplemented
    
    def locally_managed_deck_preview_view(self, resource: LocalAssetResource) -> RWidget:
        return NotImplemented
    
    def draft_list_standalone_view(self, resource: LocalResourceDraftListWindow) -> RWidget:
        return NotImplemented
    
    def image_deployment_window(self) -> RWidget:
        return NotImplemented
    
    def draft_list_deployment_window(self) -> RWidget:
        return NotImplemented
    
    def draft_list_image_preview_view(self) -> RWidget:
        return NotImplemented