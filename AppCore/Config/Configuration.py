from typing import Any, Dict, Optional, Tuple
from PyQt5.QtCore import QStandardPaths
from enum import Enum

class Configuration:
    
    APP_NAME = 'R4-MG'
    APP_VERSION = '0.11.0'
    
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
            SEARCH_SOURCE = 'search_source'
            IMAGE_SOURCE = 'image_source'

            HIDE_IMAGE_PREVIEW = 'hide_image_preview'
            SHOW_RESOURCE_DETAILS = 'show_resource_details'
            CARD_TITLE_DETAIL = 'card_title_preference'
            IS_R4_ACTION_SOUND_EFFECT_ON = 'is_r4_action_sound_effect_on'
            WINDOW_HEIGHT = 'w_height'
            WINDOW_WIDTH = 'w_width'
            WINDOW_X = 'w_x'
            WINDOW_Y = 'w_y'

            IS_MOCK_DATA = 'is_mock_data'
            IS_DELAY_NETWORK_MODE = 'is_delay_network_mode'
            IS_POPOUT_PRODUCTION_IMAGES_MODE = 'is_popout_production_images_mode'
        
        class CardTitleDetail(Enum):
            NORMAL = 0
            SHORT = 1
            DETAILED = 2
            DEFAULT = NORMAL

        class SearchSource(Enum):
            SWUDBAPI = 0
            LOCAL = 1
            DEFAULT = SWUDBAPI

        class ImageSource(Enum):
            SWUDBAPI = 0 # https://www.swu-db.com/api
            SWUDB = 1 # https://swudb.com/
            DEFAULT = SWUDBAPI
        
        def __init__(self):
            self.search_source = self.SearchSource.DEFAULT
            self.image_source = self.ImageSource.DEFAULT

            self.hide_image_preview = False
            self.show_resource_details = False
            self.cart_title_detail = self.CardTitleDetail.DEFAULT
            self.is_r4_action_sound_effect_on = False
            
            self.window_size = (None, None)
            self.window_position = (None, None)

            self.is_popout_production_images_mode = False
            self.is_mock_data = False
            self.is_delay_network_mode = False
            
        def loadJSON(self, settings: Optional[Dict[str, Any]], developer_mode: bool):
            if settings is None:
                return
            self.search_source = self.SearchSource(settings.get(self.Keys.SEARCH_SOURCE, self.SearchSource.DEFAULT))
            self.image_source = self.ImageSource(settings.get(self.Keys.IMAGE_SOURCE, self.ImageSource.DEFAULT))

            self.hide_image_preview = settings.get(self.Keys.HIDE_IMAGE_PREVIEW, False)
            self.show_resource_details = settings.get(self.Keys.SHOW_RESOURCE_DETAILS, False)
            self.cart_title_detail = self.CardTitleDetail(settings.get(self.Keys.CARD_TITLE_DETAIL, self.CardTitleDetail.DEFAULT))
            self.is_r4_action_sound_effect_on = settings.get(self.Keys.IS_R4_ACTION_SOUND_EFFECT_ON, False)
            
            self.window_size = (settings.get(self.Keys.WINDOW_WIDTH, None), settings.get(self.Keys.WINDOW_HEIGHT, None))
            self.window_position = (settings.get(self.Keys.WINDOW_X, None), settings.get(self.Keys.WINDOW_Y, None))

            self.is_mock_data = settings.get(self.Keys.IS_MOCK_DATA, False)
            self.is_delay_network_mode = settings.get(self.Keys.IS_DELAY_NETWORK_MODE, False)
            self.is_popout_production_images_mode = settings.get(self.Keys.IS_POPOUT_PRODUCTION_IMAGES_MODE, False)
            
            
            
        def toJSON(self, developer_mode: bool) -> Dict[str, Any]:
            return {
                self.Keys.SEARCH_SOURCE: self.search_source.value,
                self.Keys.IMAGE_SOURCE: self.image_source.value,

                self.Keys.HIDE_IMAGE_PREVIEW: self.hide_image_preview,
                self.Keys.SHOW_RESOURCE_DETAILS: self.show_resource_details,
                self.Keys.CARD_TITLE_DETAIL: self.cart_title_detail.value,
                self.Keys.IS_R4_ACTION_SOUND_EFFECT_ON: self.is_r4_action_sound_effect_on,
                
                self.Keys.WINDOW_WIDTH: self.window_size[0],
                self.Keys.WINDOW_HEIGHT: self.window_size[1],
                self.Keys.WINDOW_X: self.window_position[0],
                self.Keys.WINDOW_Y: self.window_position[1],
                
                self.Keys.IS_MOCK_DATA: self.is_mock_data,
                self.Keys.IS_DELAY_NETWORK_MODE: self.is_delay_network_mode,
                self.Keys.IS_POPOUT_PRODUCTION_IMAGES_MODE: self.is_popout_production_images_mode,
            }

    def __init__(self):
        self._app_name = self.APP_NAME
        self._app_ui_version = self.APP_VERSION

        self._toggles = Configuration.Toggles()
        self._settings = Configuration.Settings()

    @property
    def app_display_name(self):
        if self.is_developer_mode:
            return f"{self._app_name} [DEVELOPER MODE] - v.{self.app_ui_version}"
        else:
            return self._app_name
    
    @property
    def app_path_name(self):
        return self._app_name

    @property
    def app_ui_version(self):
        return self._app_ui_version
    
    @property
    def hide_image_preview(self) -> bool:
        return self._settings.hide_image_preview
    
    @property 
    def search_source(self) -> Settings.SearchSource:
        return self._settings.search_source

    @property 
    def image_source(self) -> Settings.ImageSource:
        return self._settings.image_source
    
    @property
    def card_title_detail(self) -> Settings.CardTitleDetail:
        return self._settings.cart_title_detail
    
    @property 
    def show_resource_details(self) -> bool:
        return self._settings.show_resource_details
    
    @property
    def is_r4_action_sound_effect_on(self) -> bool:
        return self._settings.is_r4_action_sound_effect_on
    
    @property
    def window_size(self) -> Tuple[Optional[int], Optional[int]]:
        return self._settings.window_size
    
    @property
    def picture_dir_path(self) -> str:
        # always points to picture dir
        return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation)
    
    @property
    def _config_dir_path(self) -> str:
        # will point to app name folder
        return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
    
    @property
    def _temp_dir_path(self) -> str:
        return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.TempLocation)

    @property
    def config_directory(self) -> str:
        return f'{self._config_dir_path}'
    
    @property
    def temp_dir_path(self) -> str:
        return self._temp_dir_path
    
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
        