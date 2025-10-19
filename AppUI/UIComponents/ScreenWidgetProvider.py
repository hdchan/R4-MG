
from AppCore.Models import LocalAssetResource, LocalResourceDraftListWindow
from AppUI.AppDependenciesProviding import AppDependenciesProviding
from R4UI import RWidget

from ..AppDependenciesInternalProviding import AppDependenciesInternalProviding
from ..Router.ScreenWidgetProviding import ScreenWidgetProviding
from ..UIComponents.DraftListDeployment.MainWindow import MainWindow
from ..UIComponents.ImageDeployment.Window import Window
from .CardSearchPreview import CardSearchPreviewFactory
from .DraftListDeployment.DraftListTablePackPreviewContainerStandAloneViewController import \
    DraftListTablePackPreviewContainerStandAloneViewController
from .Screens.ManageSetListViewController import ManageSetListViewController
from .Screens.ShortcutsViewController import ShortcutsViewController
from .Settings.AppSettingsViewController import AppSettingsViewController


class ScreenWidgetProvider(ScreenWidgetProviding):
    def __init__(self, 
                 app_dependencies_internal_provider: AppDependenciesInternalProviding, 
                 app_dependencies_provider: AppDependenciesProviding):
        self._app_dependencies_internal_provider = app_dependencies_internal_provider
        self._app_dependencies_provider = app_dependencies_provider
        self._external_app_dependencies_provider = app_dependencies_internal_provider.external_app_dependencies_provider
        
    @property
    def about_view(self) -> RWidget:
        return self._app_dependencies_internal_provider.external_app_dependencies_provider.provide_about_view_controller()
    
    @property
    def app_settings_view(self) -> RWidget:
        return AppSettingsViewController(self._app_dependencies_internal_provider)
    
    @property
    def shortcuts_view(self) -> RWidget:
        return ShortcutsViewController(self._app_dependencies_internal_provider)
    
    @property
    def manage_deck_list_view(self) -> RWidget:
        return ManageSetListViewController(self._app_dependencies_internal_provider)
    
    def locally_managed_deck_preview_view(self, resource: LocalAssetResource) -> RWidget:
        return CardSearchPreviewFactory.LocallyManagedSetPreviewViewController(self._app_dependencies_internal_provider, resource)
    
    def draft_list_standalone_view(self, resource: LocalResourceDraftListWindow) -> RWidget:
        return DraftListTablePackPreviewContainerStandAloneViewController(self._app_dependencies_internal_provider, resource)
    
    def image_deployment_window(self) -> RWidget:
        return Window(self._app_dependencies_internal_provider)
    
    def draft_list_deployment_window(self) -> RWidget:
        return MainWindow(self._app_dependencies_internal_provider)
    
    def draft_list_image_preview_view(self) -> RWidget:
        return self._external_app_dependencies_provider.provide_draft_list_image_preview_widget()
