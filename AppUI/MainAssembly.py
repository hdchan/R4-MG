from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget

from AppCore.Config import Configuration
from AppCore.DataSource.DataSourceRecentPublished import \
    DataSourceRecentPublished
from AppCore.DataSource.DataSourceRecentSearch import DataSourceRecentSearch
from AppCore.Models import LocalAssetResource
from AppUI.MainProgramViewController import MainProgramViewController
from AppUI.UIComponents import (CardSearchPreviewViewController,
                                ImageDeploymentListViewController,
                                ImagePreviewLocalResourceDataSourceDecorator)
from AppUI.Window import Window

from .AppDependenciesProvider import AppDependenciesProvider
from .ComponentProvider import ComponentProviding
from .UIComponents.Base.AboutViewController import AboutViewController
from .UIComponents.Base.ManageSetListViewController import \
    ManageSetListViewController
from .UIComponents.Base.SettingsViewController import SettingsViewController
from .UIComponents.Base.ShortcutsViewController import ShortcutsViewController
from .UIComponents.Composed.LocallyManagedSetPreviewViewController import LocallyManagedSetPreviewViewController
# TODO: graphing algorithm to sort dependencies?

class MainAssembly(ComponentProviding):
    
    def __init__(self):
        self.app = QApplication([])
        # Ensure this is set before config manager writes out to settings file
        self.app.setApplicationName(Configuration.APP_NAME)
        self._app_dependencies = AppDependenciesProvider(self)
        self.app.setWindowIcon(QIcon(self._app_dependencies.asset_provider.image.logo_path))
        self._style_app()

        # https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/#setting-an-application-icon
        # https://stackoverflow.com/a/35865441
        
        # https://forum.qt.io/topic/142136/how-to-change-the-application-name-pyqt5/4
        # self.app.setApplicationDisplayName(self.configuration_manager.configuration.app_display_name)
        
        self.main_window = Window(self._app_dependencies)
        
        main_widget = self._assemble_main_widget()
        
        self.main_window.setCentralWidget(main_widget)
        self.main_window.show()
        self.app.exec()
    
    
    def _style_app(self):
        custom_font = self.app.font()
        custom_font.setPointSize(10)
        self.app.setFont(custom_font)

    def _assemble_main_widget(self) -> QWidget:
        recent_published_data_source = DataSourceRecentPublished(self._app_dependencies)

        image_preview_view = ImagePreviewLocalResourceDataSourceDecorator(self._app_dependencies)
        
        card_search_view = CardSearchPreviewViewController(self._app_dependencies, 
                                                           recent_published_data_source,
                                                           image_preview_view)
        
        deployment_view = ImageDeploymentListViewController(self._app_dependencies,  
                                                            image_preview_view)

        main_program = MainProgramViewController(self._app_dependencies,
                                                card_search_view, 
                                                deployment_view)
        
        
        return main_program
    
    @property
    def about_view(self) -> QWidget:
        return AboutViewController(self._app_dependencies)
    
    @property
    def settings_view(self) -> QWidget:
        return SettingsViewController(self._app_dependencies)
    
    @property
    def shortcuts_view(self) -> QWidget:
        return ShortcutsViewController(self._app_dependencies)
    
    @property
    def manage_deck_list_view(self) -> QWidget:
        return ManageSetListViewController(self._app_dependencies)
    
    def locally_managed_deck_preview_view(self, resource: LocalAssetResource) -> QWidget:
        return LocallyManagedSetPreviewViewController(self._app_dependencies, resource)