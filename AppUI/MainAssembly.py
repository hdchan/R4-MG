from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from AppCore import *
from AppCore.ApplicationCore import ApplicationCore
from AppCore.Config import ConfigurationManager
from AppCore.Image import *
from AppCore.ImageNetwork import MockImageFetcher, RemoteImageFetcher
from AppCore.Network import *
from AppCore.Observation.ObservationTower import ObservationTower
from AppUI.Coordinators import MenuActionCoordinator, ShortcutActionCoordinator
from AppUI.MainProgramViewController import MainProgramViewController
from AppUI.UIComponents import CardSearchPreviewViewController
from AppUI.Window import Window

from .Assets import AssetProvider
from .Clients import *


class MainAssembly:

    class CoreDependencies:
        def __init__(self):
            self.observation_tower = ObservationTower()
            self.configuration_manager = ConfigurationManager(self.observation_tower)
            self.asset_provider = AssetProvider()
            self.image_resource_processor_provider = self._assemble_image_resource_processor_provider()
            self.api_client_provider = self._assemble_api_client_provider()
            self.image_source_provider = self._assemble_image_source_provider()

        def _assemble_api_client_provider(self) -> SWUDBAPIClientProvider:
            return SWUDBAPIClientProvider(self.configuration_manager, 
                                         SWUDBAPIRemoteClient(RemoteNetworker(self.configuration_manager)), 
                                         SWUDBAPILocalClient(LocalNetworker(self.configuration_manager),
                                                            self.asset_provider))
    
        def _assemble_image_resource_processor_provider(self) -> ImageResourceProcessorProviderProtocol:
            image_fetcher_provider = self._assemble_image_fetcher_provider()
            return ImageResourceProcessorProvider(ImageResourceProcessor(image_fetcher_provider,
                                                                         self.observation_tower))
        
        def _assemble_image_fetcher_provider(self) -> ImageFetcherProvider:
            return ImageFetcherProvider(self.configuration_manager, 
                                        RemoteImageFetcher(self.configuration_manager),
                                        MockImageFetcher(self.configuration_manager))
        
        def _assemble_image_source_provider(self) -> CardImageSourceProvider:
            return CardImageSourceProvider(self.configuration_manager,
                                           SWUDBAPIImageSource(),
                                           SWUDBImageSource())

    def __init__(self):
        self.app = QApplication([])
        # Ensure this is set before config manager writes out to settings file
        self.app.setApplicationName(Configuration.APP_NAME)
        self._style_app()
        
        self._core_dependencies = self.CoreDependencies()

        # https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/#setting-an-application-icon
        # https://stackoverflow.com/a/35865441
        self.app.setWindowIcon(QIcon(self._core_dependencies.asset_provider.image.logo_path))
        # https://forum.qt.io/topic/142136/how-to-change-the-application-name-pyqt5/4
        # self.app.setApplicationDisplayName(self.configuration_manager.configuration.app_display_name)
        
        main_window = Window(self._core_dependencies.configuration_manager,
                            self._core_dependencies.observation_tower, 
                            self._core_dependencies.asset_provider)
        
        main_program = self._assemble_main_program()
        main_program.load()
        
        self.menu_action_coordinator = MenuActionCoordinator(main_window,
                                                            main_program,
                                                            self._core_dependencies.configuration_manager, 
                                                            self._core_dependencies.asset_provider)
        
        self.shortcut_action_coordinator = ShortcutActionCoordinator(main_program)

        main_window.setCentralWidget(main_program)
        main_window.show()
        self.app.exec()
    
    @property
    def _configuration(self) -> Configuration:
        return self._core_dependencies.configuration_manager.configuration
    
    def _style_app(self):
        custom_font = self.app.font()
        custom_font.setPointSize(10)
        self.app.setFont(custom_font)

    def _assemble_main_program(self) -> MainProgramViewController:
        application_core = ApplicationCore(self._core_dependencies.observation_tower,
                                           self._core_dependencies.configuration_manager)
        # TODO: inject card search data source into card search view
        card_search_data_source = CardSearchDataSource(self._core_dependencies.observation_tower, 
                                                       self._core_dependencies.api_client_provider, 
                                                       self._core_dependencies.image_resource_processor_provider, 
                                                       self._core_dependencies.configuration_manager, 
                                                       self._core_dependencies.image_source_provider)
        
        card_search_view = CardSearchPreviewViewController(self._core_dependencies.observation_tower, 
                                                           self._core_dependencies.configuration_manager,
                                                           self._core_dependencies.api_client_provider,
                                                           self._core_dependencies.image_source_provider, 
                                                           self._core_dependencies.asset_provider, 
                                                           self._core_dependencies.image_resource_processor_provider)
        
        return MainProgramViewController(self._core_dependencies.observation_tower,
                                         self._core_dependencies.configuration_manager,
                                         application_core,
                                         self._core_dependencies.image_resource_processor_provider,
                                         card_search_data_source,
                                         self._core_dependencies.asset_provider,
                                         card_search_view)

    

    
    
    
        
    