
from AppCore.Models import LocalAssetResource, LocalResourceDraftListWindow
from R4UI import RWidget

class ScreenWidgetProviding:
    @property
    def about_view(self) -> RWidget:
        raise NotImplementedError
    
    def app_settings_view(self, current_tab: int = 0) -> RWidget:
        raise NotImplementedError
    
    @property
    def shortcuts_view(self) -> RWidget:
        raise NotImplementedError
    
    @property
    def manage_deck_list_view(self) -> RWidget:
        raise NotImplementedError
    
    def locally_managed_deck_preview_view(self, resource: LocalAssetResource) -> RWidget:
        raise NotImplementedError
    
    def draft_list_standalone_view(self, resource: LocalResourceDraftListWindow) -> RWidget:
        raise NotImplementedError
    
    def image_deployment_window(self) -> RWidget:
        raise NotImplementedError
    
    def draft_list_deployment_window(self) -> RWidget:
        raise NotImplementedError
    
    def draft_list_image_preview_view(self) -> RWidget:
        raise NotImplementedError