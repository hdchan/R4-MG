
from PyQt5.QtWidgets import QWidget

from AppCore.DataFetcher import *
from AppCore.DataSource.DataSourceCardSearch import *
from AppCore.DataSource.DataSourceRecentPublished import *
from AppCore.DataSource.DataSourceRecentSearch import *
from AppCore.ImageResource import *
from AppCore.Models import LocalAssetResource, LocalResourceDraftListWindow

from ..AppDependenciesProviding import *
from ..ScreenWidgetProviding import ScreenWidgetProviding
from ..UIComponents.DraftListDeployment.MainWindow import MainWindow
from ..UIComponents.ImageDeployment.Window import Window
from .Screens.Settings.AppSettingsViewController import AppSettingsViewController
from .Screens.DraftListTablePackPreviewContainerStandAloneViewController import \
    DraftListTablePackPreviewContainerStandAloneViewController
from .Screens.LocallyManagedSetPreviewViewController import \
    LocallyManagedSetPreviewViewController
from .Screens.ManageSetListViewController import ManageSetListViewController
from .Screens.ShortcutsViewController import ShortcutsViewController
from .DraftListDeployment.DraftListImagePreviewViewController import DraftListImagePreviewViewController

class ScreenWidgetProvider(ScreenWidgetProviding):
    def __init__(self, app_dependencies_provider: AppDependenciesProviding):
        self._app_dependencies_provider = app_dependencies_provider
        
    @property
    def about_view(self) -> QWidget:
        return self._app_dependencies_provider.external_app_dependencies_provider.provide_about_view_controller()
    
    @property
    def app_settings_view(self) -> QWidget:
        return AppSettingsViewController(self._app_dependencies_provider)
    
    @property
    def shortcuts_view(self) -> QWidget:
        return ShortcutsViewController(self._app_dependencies_provider)
    
    @property
    def manage_deck_list_view(self) -> QWidget:
        return ManageSetListViewController(self._app_dependencies_provider)
    
    def locally_managed_deck_preview_view(self, resource: LocalAssetResource) -> QWidget:
        return LocallyManagedSetPreviewViewController(self._app_dependencies_provider, resource)
    
    def draft_list_standalone_view(self, resource: LocalResourceDraftListWindow) -> QWidget:
        return DraftListTablePackPreviewContainerStandAloneViewController(self._app_dependencies_provider, resource)
    
    def image_deployment_window(self) -> QWidget:
        return Window(self._app_dependencies_provider)
    
    def draft_list_deployment_window(self) -> QWidget:
        return MainWindow(self._app_dependencies_provider)
    
    def draft_list_image_preview_view(self) -> QWidget:
        return DraftListImagePreviewViewController(self._app_dependencies_provider)