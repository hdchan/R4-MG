
from PyQt5.QtWidgets import QWidget

from AppCore.DataFetcher import *
from AppCore.DataSource.DataSourceCardSearch import *
from AppCore.DataSource.DataSourceRecentPublished import *
from AppCore.DataSource.DataSourceRecentSearch import *
from AppCore.ImageResource import *
from AppCore.Models import LocalAssetResource, LocalResourceDraftListWindow

from ..AppDependenciesProviding import *
from ..ScreenWidgetProviding import ScreenWidgetProviding
from .Screens.AboutViewController import AboutViewController
from .Screens.AppSettingsViewController import AppSettingsViewController
from .Screens.DraftListSettingsViewController import \
    DraftListSettingsViewController
from .Screens.SettingsContainerViewController import SettingsContainerViewController
from .Screens.DraftListTablePackPreviewContainerStandAloneViewController import \
    DraftListTablePackPreviewContainerStandAloneViewController
from .Screens.LocallyManagedSetPreviewViewController import \
    LocallyManagedSetPreviewViewController
from .Screens.ManageSetListViewController import ManageSetListViewController
from .Screens.SettingsViewController import SettingsViewController
from .Screens.ShortcutsViewController import ShortcutsViewController


class ScreenWidgetProvider(ScreenWidgetProviding):
    def __init__(self, app_dependencies_provider: AppDependenciesProviding):
        self._app_dependencies_provider = app_dependencies_provider
        
    @property
    def about_view(self) -> QWidget:
        return AboutViewController(self._app_dependencies_provider)
    
    @property
    def settings_view(self) -> QWidget:
        return SettingsViewController(self._app_dependencies_provider)
    
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
    
    def draft_list_settings_view(self) -> QWidget:
        return SettingsContainerViewController(self._app_dependencies_provider)
    
    def draft_list_standalone_view(self, resource: LocalResourceDraftListWindow) -> QWidget:
        return DraftListTablePackPreviewContainerStandAloneViewController(self._app_dependencies_provider, resource)