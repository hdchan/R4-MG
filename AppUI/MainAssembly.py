
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase
from AppCore import *
from AppCore import ApplicationCore
from AppCore.Clients import (MockImageFetcher, MockSWUDBClient,
                             RemoteImageFetcher, SWUDBClient)
from AppCore.Config import ConfigurationManager
from AppCore.Data import APIClientProvider
from AppCore.Image import ImageFetcherProvider
from AppCore.Network import *
from AppCore.Observation.ObservationTower import ObservationTower
from AppUI.Coordinators import MenuActionCoordinator, ShortcutActionCoordinator
from AppUI.MainProgramViewController import MainProgramViewController
from AppUI.Window import Window


class MainAssembly:
    def __init__(self):
        self.app = QApplication([])
        self._style_app()
        self.configuration = Configuration()
        # Ensure this is set before config manager writes out to settings file
        self.app.setApplicationName(self.configuration.app_path_name)
        observation_tower = ObservationTower()
        configuration_manager = ConfigurationManager(observation_tower, 
                                                     self.configuration)
        self.networker = Networker(self.configuration)
        api_client_provider = self._assemble_api_client_provider()
        image_fetcher_provider = self._assemble_image_fetcher_provider()
        
        application_core = ApplicationCore(observation_tower, 
                                        api_client_provider, 
                                        image_fetcher_provider, 
                                        self.configuration)
        main_window = Window(self.configuration, 
                            observation_tower)
        main_program = MainProgramViewController(observation_tower,
                                                self.configuration,
                                                application_core)
        self.menu_action_coordinator = MenuActionCoordinator(main_window,
                                                        main_program,
                                                        application_core.resource_deployer,
                                                        configuration_manager)
        self.shortcut_action_coordinator = ShortcutActionCoordinator(main_program)
        main_program.load()
        main_window.setCentralWidget(main_program)
        main_window.show()
        self.app.exec()
    
    def _style_app(self):
        # db = QFontDatabase()
        # styles = db.styles("Roboto")
        custom_font = self.app.font()
        # custom_font = db.font("Medium", "Medium Italic", 16)
        # custom_font.setFamily("Roboto")
        custom_font.setPointSize(10)
        self.app.setFont(custom_font)
    
    def _assemble_api_client_provider(self) -> APIClientProvider:
        return APIClientProvider(self.configuration, 
                                 SWUDBClient(self.networker), 
                                 MockSWUDBClient(MockNetworker(self.configuration)))
    
    def _assemble_image_fetcher_provider(self) -> ImageFetcherProvider:
        return ImageFetcherProvider(self.configuration, 
                                    RemoteImageFetcher(self.configuration),
                                    MockImageFetcher(self.configuration))