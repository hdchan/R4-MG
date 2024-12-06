from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from AppCore import *
from AppCore.ApplicationCore import ApplicationCore
from AppCore.Config import ConfigurationManager
from AppCore.Image import *
from AppCore.ImageNetwork import MockImageFetcher, RemoteImageFetcher
from AppCore.Network import *
from AppCore.Observation.ObservationTower import ObservationTower
from AppUI.AdvancedViewController import AdvancedViewController
from AppUI.ContainerViewController import ContainerViewController
from AppUI.Coordinators import MenuActionCoordinator, ShortcutActionCoordinator
from AppUI.MainProgramViewController import MainProgramViewController
from AppUI.Window import Window

from .Assets import AssetProvider
from .Clients import *


class MainAssembly:
    def __init__(self):
        self.app = QApplication([])
        
        # Ensure this is set before config manager writes out to settings file
        self.app.setApplicationName(Configuration.APP_NAME)
        self._style_app()
        self.observation_tower = ObservationTower()
        self.configuration_manager = ConfigurationManager(self.observation_tower)
        self.asset_provider = AssetProvider()

        # https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/#setting-an-application-icon
        # https://stackoverflow.com/a/35865441
        self.app.setWindowIcon(QIcon(self.asset_provider.image.logo_path))
        # https://forum.qt.io/topic/142136/how-to-change-the-application-name-pyqt5/4
        # self.app.setApplicationDisplayName(self.configuration_manager.configuration.app_display_name)
        
        api_client_provider = self._assemble_api_client_provider()
        
        image_source_provider = self._assemble_image_source_provider()
        image_resource_processor_provider = self._assemble_image_resource_processor_provider()
        application_core = ApplicationCore(self.observation_tower, 
                                           image_resource_processor_provider, 
                                           image_source_provider,
                                           self.configuration_manager)
        main_window = Window(self.configuration_manager,
                            self.configuration_manager,
                            self.observation_tower, 
                            self.asset_provider)
        card_search_data_source = CardSearchDataSource(self.observation_tower, 
                                                       api_client_provider, 
                                                       image_resource_processor_provider, 
                                                       self.configuration_manager, 
                                                       image_source_provider)
        main_program = MainProgramViewController(self.observation_tower,
                                                self.configuration_manager,
                                                application_core,
                                                api_client_provider,
                                                image_source_provider,
                                                image_resource_processor_provider,
                                                card_search_data_source,
                                                self.asset_provider)
        advanced_view = AdvancedViewController(self.observation_tower, 
                                               application_core)
        self.menu_action_coordinator = MenuActionCoordinator(main_window,
                                                            main_program,
                                                            self.configuration_manager, 
                                                            self.asset_provider)
        
        self.shortcut_action_coordinator = ShortcutActionCoordinator(main_program)
        main_program.load()
        container = ContainerViewController(main_program, 
                                            advanced_view, 
                                            self.configuration_manager, 
                                            self.observation_tower)
        main_window.setCentralWidget(container)
        main_window.show()
        self.app.exec()
    
    @property
    def _configuration(self) -> Configuration:
        return self.configuration_manager.configuration
    
    def _style_app(self):
        # db = QFontDatabase()
        # styles = db.styles("Roboto")
        custom_font = self.app.font()
        # custom_font = db.font("Medium", "Medium Italic", 16)
        # custom_font.setFamily("Roboto")
        custom_font.setPointSize(10)
        self.app.setFont(custom_font)

    def _assemble_image_resource_processor_provider(self) -> ImageResourceProcessorProviderProtocol:
        image_fetcher_provider = self._assemble_image_fetcher_provider()
        return ImageResourceProcessorProvider(ImageResourceProcessor(image_fetcher_provider,
                                                                    self.observation_tower))

    def _assemble_api_client_provider(self) -> SWUDBAPIClientProvider:
        return SWUDBAPIClientProvider(self.configuration_manager, 
                                 SWUDBAPIRemoteClient(RemoteNetworker(self.configuration_manager)), 
                                 SWUDBAPILocalClient(LocalNetworker(self.configuration_manager), 
                                                 self.asset_provider))
    
    def _assemble_image_fetcher_provider(self) -> ImageFetcherProvider:
        return ImageFetcherProvider(self.configuration_manager, 
                                    RemoteImageFetcher(self.configuration_manager),
                                    MockImageFetcher(self.configuration_manager))
        
    def _assemble_image_source_provider(self) -> CardImageSourceProvider:
        return CardImageSourceProvider(self.configuration_manager,
                                       SWUDBAPIImageSource(),
                                       SWUDBImageSource())