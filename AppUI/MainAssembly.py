
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication

from AppCore import *
from AppCore import ApplicationCore
from AppCore.Clients import (APIClientProvider, CardImageSourceProvider,
                             MockSWUDBClient, SWUDBAPIImageSource, SWUDBClient,
                             SWUDBImageSource)
from AppCore.Config import ConfigurationManager
from AppCore.Image import ImageFetcherProvider
from AppCore.ImageNetwork import MockImageFetcher, RemoteImageFetcher
from AppCore.Network import *
from AppCore.Observation.ObservationTower import ObservationTower
from AppUI.AdvancedViewController import AdvancedViewController
from AppUI.ContainerViewController import ContainerViewController
from AppUI.Coordinators import MenuActionCoordinator, ShortcutActionCoordinator
from AppUI.MainProgramViewController import MainProgramViewController
from AppUI.Window import Window

from .Assets import AssetProvider
from .Coordinators.AboutViewController import AboutViewController


class MainAssembly:
    def __init__(self):
        self.app = QApplication([])
        # Ensure this is set before config manager writes out to settings file
        self.app.setApplicationName(Configuration.APP_NAME)
        self._style_app()
        observation_tower = ObservationTower()
        self.configuration_manager = ConfigurationManager(observation_tower)
        asset_provider = AssetProvider()
        
        self.networker = Networker(self.configuration_manager)
        api_client_provider = self._assemble_api_client_provider()
        image_fetcher_provider = self._assemble_image_fetcher_provider()
        image_source_provider = self._assemble_image_source_provider()
        application_core = ApplicationCore(observation_tower, 
                                        api_client_provider, 
                                        image_fetcher_provider, 
                                        image_source_provider,
                                        self.configuration_manager)
        main_window = Window(self.configuration_manager, 
                            observation_tower, 
                            asset_provider)
        main_program = MainProgramViewController(observation_tower,
                                                self.configuration_manager,
                                                application_core,
                                                api_client_provider,
                                                image_source_provider, 
                                                asset_provider)
        advanced_view = AdvancedViewController(observation_tower, 
                                               application_core)
        self.menu_action_coordinator = MenuActionCoordinator(main_window,
                                                        main_program,
                                                        application_core,
                                                        self.configuration_manager, 
                                                        asset_provider)
        
        self.shortcut_action_coordinator = ShortcutActionCoordinator(main_program)
        main_program.load()
        container = ContainerViewController(main_program, 
                                            advanced_view, 
                                            self.configuration_manager, 
                                            observation_tower)
        main_window.setCentralWidget(container)
        main_window.show()
        # main_window.setStyleSheet(f'''
        #                    .QWidget {{background-image: url("C://Users//henry//Documents//code//R4-MG//AppUI//Assets//Images//large_spark_of_rebellion_starfield_c4fdfaa6a7.png");
        #                    background-position: center;}}
        #                    ''')
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
    
    def _assemble_api_client_provider(self) -> APIClientProvider:
        return APIClientProvider(self.configuration_manager, 
                                 SWUDBClient(self.networker), 
                                 MockSWUDBClient(MockNetworker(self.configuration_manager)))
    
    def _assemble_image_fetcher_provider(self) -> ImageFetcherProvider:
        return ImageFetcherProvider(self.configuration_manager, 
                                    RemoteImageFetcher(self.configuration_manager),
                                    MockImageFetcher(self.configuration_manager))
        
    def _assemble_image_source_provider(self) -> CardImageSourceProvider:
        return CardImageSourceProvider(self.configuration_manager,
                                       SWUDBAPIImageSource(),
                                       SWUDBImageSource())