from typing import Any, Dict, Optional
from PyQt5.QtCore import QStandardPaths
from enum import Enum

class Configuration:
    
    APP_NAME = 'R4-MG'
    
    class Toggles:
        class Keys:
            DEVELOPER_MODE = 'developer_mode'
            
        def __init__(self):
            self.developer_mode = False
        
        def loadJSON(self, toggles: Optional[Dict[str, Any]]):
            if toggles is None:
                return
            self.developer_mode = toggles.get(self.Keys.DEVELOPER_MODE, False)
            
        def toJSON(self) -> Dict[str, Any]:
            return {
                self.Keys.DEVELOPER_MODE: self.developer_mode
            }
            
    class Settings:
        class Keys:
            IS_PERFORMANCE_MODE = 'is_performance_mode'
            IS_MOCK_DATA = 'is_mock_data'
            IS_DELAY_NETWORK_MODE = 'is_delay_network_mode'
            IS_POPOUT_PRODUCTION_IMAGES_MODE = 'is_popout_production_images_mode'
            IMAGE_SOURCE = 'image_source'
            SHOW_RESOURCE_DETAILS = 'show_resource_details'
            
        class ImageSource(Enum):
            SWUDBAPI = 0 # https://www.swu-db.com/api
            SWUDB = 1 # https://swudb.com/
        
        def __init__(self):
            self.is_performance_mode = False
            self.is_popout_production_images_mode = False
            self.is_mock_data = False
            self.is_delay_network_mode = False
            self.image_source = self.ImageSource.SWUDBAPI
            self.show_resource_details = False
            
        def loadJSON(self, settings: Optional[Dict[str, Any]], developer_mode: bool):
            if settings is None:
                return
            
            self.is_performance_mode = settings.get(self.Keys.IS_PERFORMANCE_MODE, False)
            self.is_mock_data = settings.get(self.Keys.IS_MOCK_DATA, False)
            self.is_delay_network_mode = settings.get(self.Keys.IS_DELAY_NETWORK_MODE, False)
            self.is_popout_production_images_mode = settings.get(self.Keys.IS_POPOUT_PRODUCTION_IMAGES_MODE, False)
            self.image_source = self.ImageSource(settings.get(self.Keys.IMAGE_SOURCE, 0))
            self.show_resource_details = settings.get(self.Keys.SHOW_RESOURCE_DETAILS, False)
            
        def toJSON(self, developer_mode: bool) -> Dict[str, Any]:
            return {
                self.Keys.IS_PERFORMANCE_MODE: self.is_performance_mode,
                self.Keys.IS_MOCK_DATA: self.is_mock_data,
                self.Keys.IS_DELAY_NETWORK_MODE: self.is_delay_network_mode,
                self.Keys.IS_POPOUT_PRODUCTION_IMAGES_MODE: self.is_popout_production_images_mode,
                self.Keys.IMAGE_SOURCE: self.image_source.value,
                self.Keys.SHOW_RESOURCE_DETAILS: self.show_resource_details
            }

    def __init__(self):
        self._app_name = self.APP_NAME
        self._app_ui_version = '0.7.0'

        self._toggles = Configuration.Toggles()
        self._settings = Configuration.Settings()

    @property
    def app_display_name(self):
        if self.is_developer_mode:
            return self._app_name + " [DEVELOPER MODE]"
        else:
            return self._app_name
    
    @property
    def app_path_name(self):
        return self._app_name

    @property
    def app_ui_version(self):
        return self._app_ui_version
    
    @property
    def is_performance_mode(self) -> bool:
        return self._settings.is_performance_mode
    
    @property 
    def image_source(self) -> Settings.ImageSource:
        return self._settings.image_source
    
    @property 
    def show_resource_details(self) -> bool:
        return self._settings.show_resource_details
    
    @property
    def picture_dir_path(self) -> str:
        # always points to picture dir
        return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation)
    
    @property
    def _config_dir_path(self) -> str:
        # will point to app name folder
        return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
    
    @property
    def config_directory(self) -> str:
        return f'{self._config_dir_path}'
    
    @property
    def production_file_path(self) -> str:
        return f'{self.picture_dir_path}/{self.app_path_name}/production/'
    
    @property
    def production_preview_file_path(self) -> str:
        return f'{self.production_file_path}preview/'
    
    @property
    def cache_file_path(self) -> str:
        return f'{self.picture_dir_path}/{self.app_path_name}/cache/' 
    
    @property
    def cache_preview_file_path(self) -> str:
        return f'{self.cache_file_path}preview/'

    # MARK: - Developer settings

    @property
    def is_developer_mode(self) -> bool:
        return self._toggles.developer_mode

    @property
    def is_mock_data(self) -> bool:
        return self.is_developer_mode and self._settings.is_mock_data
        
    @property
    def is_delay_network_mode(self) -> bool:
        return self.is_developer_mode and self._settings.is_delay_network_mode
        
    @property
    def network_delay_duration(self) -> int:
        if self.is_delay_network_mode:
            return 5
        else:
            return 0
        
    @property
    def is_popout_production_images_mode(self) -> bool:
        return self._settings.is_popout_production_images_mode
    
    @is_popout_production_images_mode.setter
    def is_popout_production_images_mode(self, value: bool):
        self._settings.is_popout_production_images_mode = value
        

    class Keys:
        TOGGLES = 'toggles'
        SETTINGS = 'settings'

    def loadJSON(self, json: Dict[str, Any]):
        self._toggles.loadJSON(json.get(self.Keys.TOGGLES, {}))
        self._settings.loadJSON(json.get(self.Keys.SETTINGS, {}), self._toggles.developer_mode)
        
    def toJSON(self) -> Dict[str, Any]:
        return {
            self.Keys.TOGGLES: self._toggles.toJSON(),
            self.Keys.SETTINGS: self._settings.toJSON(self._toggles.developer_mode)
        }
        
class ConfigurationProvider:
    @property
    def configuration(self) -> Configuration:
        return NotImplemented