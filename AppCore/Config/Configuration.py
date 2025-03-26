from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from PyQt5.QtCore import QStandardPaths

"""
1. Add Key
2. Add to default value
3. Create getter
4. Create setter
"""
class Configuration:
    
    APP_NAME = 'R4-MG'
    APP_VERSION = '0.14.2'
    SETTINGS_VERSION = '1.0'
    
    class Toggles:
        class Keys:
            DEVELOPER_MODE = 'developer_mode'

    class Settings:
        class Keys:
            SEARCH_SOURCE = 'search_source'
            IMAGE_SOURCE = 'image_source'

            IMAGE_CACHE_LIFE_IN_DAYS = 'image_cache_life_in_days'
            SEARCH_HISTORY_CACHE_LIFE_IN_DAYS = 'search_history_cache_life_in_days'
            PUBLISH_HISTORY_CACHE_LIFE_IN_DAYS = 'publish_history_cache_life_in_days'

            HIDE_IMAGE_PREVIEW = 'hide_image_preview'
            SHOW_RESOURCE_DETAILS = 'show_resource_details'
            HIDE_DEPLOYMENT_CELL_CONTROLS = 'hide_deployment_cell_controls'

            CARD_TITLE_DETAIL = 'card_title_preference'

            WINDOW_HEIGHT = 'w_height'
            WINDOW_WIDTH = 'w_width'
            
            RESIZE_PROD_IMAGES = 'resize_prod_images'
            RESIZE_PROD_IMAGES_MAX_SIZE = 'resize_prod_images_max_size'
            
            DEPLOYMENT_LIST_SORT_CRITERIA = 'deployment_list_sort_criteria'
            DEPLOYMENT_LIST_IS_DESCENDING_ORDER = 'deployment_list_is_descending_order'

            IS_MOCK_DATA = 'is_mock_data'
            IS_DELAY_NETWORK_MODE = 'is_delay_network_mode'
        
        class ImageCacheLifeInDays(int, Enum):
            NEVER = -1
            ALWAYS = 0
            DEFAULT = NEVER

        class SearchHistoryCacheLifeInDays(int, Enum):
            MIN = 0
            DEFAULT = 14
        
        class PublishHistoryCacheLifeInDays(int, Enum):
            MIN = 0
            DEFAULT = 14

        class CardTitleDetail(int, Enum):
            NORMAL = 0
            SHORT = 1
            DETAILED = 2
            DEFAULT = NORMAL

        class SearchSource(int, Enum):
            SWUDBAPI = 0
            LOCAL = 1
            STARWARSUNLIMITED_FFG = 2
            DEFAULT = STARWARSUNLIMITED_FFG

        class ImageSource(int, Enum):
            SWUDBAPI = 0 # https://www.swu-db.com/api
            SWUDB = 1 # https://swudb.com/
            CUSTOM_LOCAL = 99
            DEFAULT = SWUDBAPI
            
        class DeploymentListSortCriteria(int, Enum):
            FILE_NAME = 0
            CREATED_DATE = 1
            CUSTOM = 99
            DEFAULT = FILE_NAME
            
    class Keys:
        TOGGLES = 'toggles'
        SETTINGS = 'settings'
    
    @classmethod
    def default(cls):
        obj = cls.__new__(cls)
        underlying_json: Dict[str, Any] = {
            Configuration.Keys.TOGGLES: {
                Configuration.Toggles.Keys.DEVELOPER_MODE: False
            },
            Configuration.Keys.SETTINGS: {
                Configuration.Settings.Keys.SEARCH_SOURCE: Configuration.Settings.SearchSource.DEFAULT.value,
                Configuration.Settings.Keys.IMAGE_SOURCE: Configuration.Settings.ImageSource.DEFAULT.value,

                Configuration.Settings.Keys.IMAGE_CACHE_LIFE_IN_DAYS: Configuration.Settings.ImageCacheLifeInDays.DEFAULT.value,
                Configuration.Settings.Keys.SEARCH_HISTORY_CACHE_LIFE_IN_DAYS: Configuration.Settings.SearchHistoryCacheLifeInDays.DEFAULT.value,
                Configuration.Settings.Keys.PUBLISH_HISTORY_CACHE_LIFE_IN_DAYS: Configuration.Settings.PublishHistoryCacheLifeInDays.DEFAULT.value,

                Configuration.Settings.Keys.HIDE_IMAGE_PREVIEW: False,
                Configuration.Settings.Keys.SHOW_RESOURCE_DETAILS: False,
                Configuration.Settings.Keys.HIDE_DEPLOYMENT_CELL_CONTROLS: False,
                Configuration.Settings.Keys.CARD_TITLE_DETAIL: Configuration.Settings.CardTitleDetail.DEFAULT.value,
                
                Configuration.Settings.Keys.WINDOW_HEIGHT: None,
                Configuration.Settings.Keys.WINDOW_WIDTH: None,
                
                Configuration.Settings.Keys.RESIZE_PROD_IMAGES: False,
                Configuration.Settings.Keys.RESIZE_PROD_IMAGES_MAX_SIZE: 256,
                
                Configuration.Settings.Keys.DEPLOYMENT_LIST_SORT_CRITERIA: Configuration.Settings.DeploymentListSortCriteria.DEFAULT.value,
                Configuration.Settings.Keys.DEPLOYMENT_LIST_IS_DESCENDING_ORDER: False, 
                
                Configuration.Settings.Keys.IS_MOCK_DATA: False,
                Configuration.Settings.Keys.IS_DELAY_NETWORK_MODE: False
            }
        }
        super(Configuration, obj).__init__()
        obj._app_name = Configuration.APP_NAME
        obj._app_ui_version = Configuration.APP_VERSION
        obj._underlying_json = underlying_json
        obj.__default_config_json = underlying_json
        return obj
    
    def __init__(self, underlying_json: Dict[str, Any]):
        self._app_name = self.APP_NAME
        self._app_ui_version = self.APP_VERSION
        self._settings_version = self.SETTINGS_VERSION
        self._underlying_json = underlying_json

        default_config = Configuration.default()
        self.__default_config_json: Dict[str, Any] = default_config._underlying_json

        assert(default_config.is_developer_mode is False)
        assert(self._underlying_json is not None)
        assert(self.__default_config_json is not None)
     
    def to_data(self) -> Dict[str, Any]:
        return self._underlying_json

    @property
    def app_display_name(self):
        if self.is_developer_mode:
            return f"{self._app_name} [DEVELOPER MODE] - v.{self.app_ui_version}"
        else:
            return f"{self._app_name} - v.{self.app_ui_version}"
    
    @property
    def app_path_name(self):
        return self._app_name

    @property
    def app_ui_version(self):
        return self._app_ui_version
    
    @property
    def _settings(self) -> Dict[str, Any]:
        return self._get_with_default(self.Keys.SETTINGS)

    @property
    def _toggles(self) -> Dict[str, Any]:
        return self._get_with_default(self.Keys.TOGGLES)
    

    # MARK: - User settings
    @property
    def hide_image_preview(self) -> bool:
        return self._get_with_default_settings(self.Settings.Keys.HIDE_IMAGE_PREVIEW)
    
    @property
    def hide_deployment_cell_controls(self) -> bool:
        return self._get_with_default_settings(self.Settings.Keys.HIDE_DEPLOYMENT_CELL_CONTROLS)

    @property 
    def search_source(self) -> Settings.SearchSource:
        return self.Settings.SearchSource(self._get_with_default_settings(self.Settings.Keys.SEARCH_SOURCE))

    @property 
    def image_source(self) -> Settings.ImageSource:
        return self.Settings.ImageSource(self._get_with_default_settings(self.Settings.Keys.IMAGE_SOURCE))
    
    @property
    def card_title_detail(self) -> Settings.CardTitleDetail:
        return self.Settings.CardTitleDetail(self._get_with_default_settings(self.Settings.Keys.CARD_TITLE_DETAIL))
    
    @property 
    def show_resource_details(self) -> bool:
        return self._get_with_default_settings(self.Settings.Keys.SHOW_RESOURCE_DETAILS)
    
    @property
    def window_size(self) -> Optional[Tuple[int, int]]:
        if (self._get_with_default_settings(self.Settings.Keys.WINDOW_HEIGHT) is not None and 
            self._get_with_default_settings(self.Settings.Keys.WINDOW_WIDTH) is not None):
            return (self._get_with_default_settings(self.Settings.Keys.WINDOW_HEIGHT), self._get_with_default_settings(self.Settings.Keys.WINDOW_WIDTH))
        return None
    
    @property
    def resize_prod_images(self) -> bool:
        return self._get_with_default_settings(self.Settings.Keys.RESIZE_PROD_IMAGES)
    
    @property
    def resize_prod_images_max_size(self) -> int:
        return self._get_with_default_settings(self.Settings.Keys.RESIZE_PROD_IMAGES_MAX_SIZE)
    
    @property
    def deployment_list_sort_criteria(self) -> Settings.DeploymentListSortCriteria:
        return self.Settings.DeploymentListSortCriteria(self._get_with_default_settings(self.Settings.Keys.DEPLOYMENT_LIST_SORT_CRITERIA))

    @property
    def deployment_list_sort_is_desc_order(self) -> bool:
        return self._get_with_default_settings(self.Settings.Keys.DEPLOYMENT_LIST_IS_DESCENDING_ORDER)
    
    @property
    def image_cache_life_in_days(self) -> int:
        return self._get_with_default_settings(self.Settings.Keys.IMAGE_CACHE_LIFE_IN_DAYS)
    
    @property
    def search_history_cache_life_in_days(self) -> int:
        return self._get_with_default_settings(self.Settings.Keys.SEARCH_HISTORY_CACHE_LIFE_IN_DAYS)
    
    @property
    def publish_history_cache_life_in_days(self) -> int:
        return self._get_with_default_settings(self.Settings.Keys.PUBLISH_HISTORY_CACHE_LIFE_IN_DAYS)


    # MARK: - Developer settings
    @property
    def is_developer_mode(self) -> bool:
        return self._get_with_default_toggles(self.Toggles.Keys.DEVELOPER_MODE)

    @property
    def is_mock_data(self) -> bool:
        return self.is_developer_mode and self._get_with_default_settings(self.Settings.Keys.IS_MOCK_DATA)
        
    @property
    def is_delay_network_mode(self) -> bool:
        return self.is_developer_mode and self._get_with_default_settings(self.Settings.Keys.IS_DELAY_NETWORK_MODE)
        
    @property
    def network_delay_duration(self) -> int:
        if self.is_delay_network_mode:
            return 5
        else:
            return 0
        
    # MARK: - file paths
    @property
    def _picture_dir_path(self) -> str:
        # always points to picture dir
        # append app name
        return f'{QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation)}/{self.app_path_name}'
    
    @property
    def _config_dir_path(self) -> str:
        # will point to app name folder
        return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
    
    @property
    def _temp_dir_path(self) -> str:
        return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.TempLocation)

    @property
    def publish_history_path(self) -> str:
        return f'{self._picture_dir_path}/publish_history.json'
    
    @property
    def search_history_path(self) -> str:
        return f'{self._picture_dir_path}/search_history.json'

    @property
    def config_directory(self) -> str:
        return f'{self._config_dir_path}'
    
    @property
    def temp_dir_path(self) -> str:
        return self._temp_dir_path
    
    @property
    def production_dir_path(self) -> str:
        return f'{self._picture_dir_path}/production/'
    
    @property
    def production_preview_dir_path(self) -> str:
        return f'{self.production_dir_path}preview/'
    
    @property
    def cache_dir_path(self) -> str:
        return f'{self._picture_dir_path}/cache/' 
    
    @property
    def cache_preview_dir_path(self) -> str:
        return f'{self.cache_dir_path}preview/'
    
    # MARK: - Helpers
    '''
    Convenience method to set default value based on path and return.
    Will recursively set default value if path does not exist.
    '''
    def _get_with_default(self, key: str, path: List[str] = []) -> Any:
        under: Dict[str, Any] = self._underlying_json
        default: Dict[str, Any] = self.__default_config_json
        traversed: List[str] = []
        for p in path:
            if p not in under:
                self._get_with_default(p, traversed)
            under = under[p]
            default = default[p]
            traversed.append(p)
        if key not in under:
            under[key] = default[key]
        return under[key]
    
    def _get_with_default_settings(self, key: str) -> Any:
        return self._get_with_default(key, [self.Keys.SETTINGS])
    
    def _get_with_default_toggles(self, key: str) -> Any:
        return self._get_with_default(key, [self.Keys.TOGGLES])
    
class MutableConfiguration(Configuration):
    
    # MARK - User settings
    def set_hide_image_preview(self, value: bool):
        self._settings[self.Settings.Keys.HIDE_IMAGE_PREVIEW] = value

    def set_hide_deployment_cell_controls(self, value: bool):
        self._settings[self.Settings.Keys.HIDE_DEPLOYMENT_CELL_CONTROLS] = value
        
    def set_search_source(self, source: Configuration.Settings.SearchSource):
        self._settings[self.Settings.Keys.SEARCH_SOURCE] = source.value

    def set_image_source(self, source: Configuration.Settings.ImageSource):
        self._settings[self.Settings.Keys.IMAGE_SOURCE] = source.value

    def set_show_resource_details(self, value: bool):
        self._settings[self.Settings.Keys.SHOW_RESOURCE_DETAILS] = value

    def set_card_title_detail(self, detail: Configuration.Settings.CardTitleDetail):
        self._settings[self.Settings.Keys.CARD_TITLE_DETAIL] = detail.value
        
    def set_window_size(self, size: Tuple[int, int]):
        self._settings[self.Settings.Keys.WINDOW_HEIGHT] = size[0]
        self._settings[self.Settings.Keys.WINDOW_WIDTH] = size[1]

    def reset_window_size(self):
        self._settings[self.Settings.Keys.WINDOW_HEIGHT] = None
        self._settings[self.Settings.Keys.WINDOW_WIDTH] = None
        
    def set_resize_prod_images(self, value: bool):
        self._settings[self.Settings.Keys.RESIZE_PROD_IMAGES] = value
        
    def set_resize_prod_images_max_size(self, value: int):
        actual_value = value
        if value < 256:
            actual_value = 256
        # TODO: throw exception if outside bounds?
        self._settings[self.Settings.Keys.RESIZE_PROD_IMAGES_MAX_SIZE] = actual_value
        
    def set_deployment_list_sort_criteria(self, criteria: Configuration.Settings.DeploymentListSortCriteria):
        self._settings[self.Settings.Keys.DEPLOYMENT_LIST_SORT_CRITERIA] = criteria.value
        
    def set_deployment_list_sort_order(self, is_desc_order :bool):
        self._settings[self.Settings.Keys.DEPLOYMENT_LIST_IS_DESCENDING_ORDER] = is_desc_order

    def set_image_cache_life_in_days(self, value: int):
        self._settings[self.Settings.Keys.IMAGE_CACHE_LIFE_IN_DAYS] = value

    def set_search_history_cache_life_in_days(self, value: int):
        self._settings[self.Settings.Keys.SEARCH_HISTORY_CACHE_LIFE_IN_DAYS] = value

    def set_publish_history_cache_life_in_days(self, value: int):
        self._settings[self.Settings.Keys.PUBLISH_HISTORY_CACHE_LIFE_IN_DAYS] = value
        
    # MARK: - Developer settings
    def set_is_mock_data(self, value: bool):
        self._settings[self.Settings.Keys.IS_MOCK_DATA] = value
        
    def set_is_delay_network_mode(self, value: bool):
        self._settings[self.Settings.Keys.IS_DELAY_NETWORK_MODE] = value