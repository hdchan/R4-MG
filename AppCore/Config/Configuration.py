from enum import Enum
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QStandardPaths

"""
1. Add Key
2. Add to default value
3. Create getter
4. Create setter
"""
class Configuration():
    
    APP_NAME = 'R4-MG'
    APP_VERSION = '0.24.0'
    SETTINGS_VERSION = '1.0'
    
    class Toggles:
        class Keys:
            DEVELOPER_MODE = 'developer_mode'
            DRAFT_LIST_IMAGE_PREVIEW = 'draft_list_image_preview'
            REMOTE_SOCKET_CONNECTION = "remote_socket_connection"
            USES_LEGACY_DECK_IMAGE_GENERATION = 'uses_legacy_deck_image_generation'

    class Settings:
        class Keys:
            SEARCH_SOURCE = 'search_source'

            CUSTOM_DIRECTORY_SEARCH_PATH = 'custom_directory_search_path'

            IMAGE_CACHE_LIFE_IN_DAYS = 'image_cache_life_in_days'

            HIDE_IMAGE_PREVIEW = 'hide_image_preview'
            IMAGE_PREVIEW_SCALE = 'image_preview_scale'
            SHOW_RESOURCE_DETAILS = 'show_resource_details'
            HIDE_DEPLOYMENT_CELL_CONTROLS = 'hide_deployment_cell_controls'
            IS_DEPLOYMENT_LIST_HORIZONTAL = 'is_deployment_list_horizontal'

            CARD_TITLE_DETAIL = 'card_title_preference'
            
            RESIZE_PROD_IMAGES = 'resize_prod_images'
            RESIZE_PROD_IMAGES_MAX_SIZE = 'resize_prod_images_max_size'
            
            DEPLOYMENT_LIST_SORT_CRITERIA = 'deployment_list_sort_criteria'
            DEPLOYMENT_LIST_IS_DESCENDING_ORDER = 'deployment_list_is_descending_order'
            
            DRAFT_LIST_STYLES = 'draft_list_styles'
            DRAFT_LIST_ADD_CARD_MODE = 'draft_list_add_card_mode'
            DRAFT_LIST_ADD_CARD_DEPLOYMENT_DESTINATION = 'draft_list_add_card_deployment_destination'
            
            REMOTE_SOCKET_URL = 'remote_socket_url'

            IS_MOCK_DATA = 'is_mock_data'
            IS_DELAY_NETWORK_MODE = 'is_delay_network_mode'
        
        class ImageCacheLifeInDays(int, Enum):
            NEVER = -1
            ALWAYS = 0
            DEFAULT = NEVER

        class CardTitleDetail(int, Enum):
            NORMAL = 0
            SHORT = 1
            DETAILED = 2
            DEFAULT = NORMAL

        class SearchSource(int, Enum):
            SWUDBAPI = 0
            LOCAL = 1 # NOTE: keep but dont reuse
            STARWARSUNLIMITED_FFG = 2
            LOCALLY_MANAGED_DECKS = 3
            DEFAULT = SWUDBAPI
            
        class DeploymentListSortCriteria(int, Enum):
            FILE_NAME = 0
            CREATED_DATE = 1
            CUSTOM = 99
            DEFAULT = FILE_NAME
            
        class DraftListAddCardMode(int, Enum):
            OFF = 0
            STAGE = 1
            STAGE_AND_PUBLISH = 2
            DEFAULT = OFF
            
    class Keys:
        TOGGLES = 'toggles'
        SETTINGS = 'settings'
    
    def __eq__(self, other):  # type: ignore
        if not isinstance(other, Configuration):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self._underlying_json == other._underlying_json
    
    @classmethod
    def default(cls):
        obj = cls.__new__(cls)
        underlying_json: Dict[str, Any] = {
            Configuration.Keys.TOGGLES: {
                Configuration.Toggles.Keys.DEVELOPER_MODE: False,
                Configuration.Toggles.Keys.DRAFT_LIST_IMAGE_PREVIEW: False,
                Configuration.Toggles.Keys.REMOTE_SOCKET_CONNECTION: False,
                Configuration.Toggles.Keys.USES_LEGACY_DECK_IMAGE_GENERATION: False
            },
            Configuration.Keys.SETTINGS: {
                Configuration.Settings.Keys.SEARCH_SOURCE: Configuration.Settings.SearchSource.DEFAULT.value,
                
                Configuration.Settings.Keys.CUSTOM_DIRECTORY_SEARCH_PATH: None,

                Configuration.Settings.Keys.IMAGE_CACHE_LIFE_IN_DAYS: Configuration.Settings.ImageCacheLifeInDays.DEFAULT.value,

                Configuration.Settings.Keys.HIDE_IMAGE_PREVIEW: False,
                Configuration.Settings.Keys.IMAGE_PREVIEW_SCALE: 1.0,
                Configuration.Settings.Keys.SHOW_RESOURCE_DETAILS: False,
                Configuration.Settings.Keys.HIDE_DEPLOYMENT_CELL_CONTROLS: False,
                Configuration.Settings.Keys.CARD_TITLE_DETAIL: Configuration.Settings.CardTitleDetail.DEFAULT.value,
                Configuration.Settings.Keys.IS_DEPLOYMENT_LIST_HORIZONTAL: False,

                
                Configuration.Settings.Keys.RESIZE_PROD_IMAGES: False,
                Configuration.Settings.Keys.RESIZE_PROD_IMAGES_MAX_SIZE: 256,
                
                Configuration.Settings.Keys.DEPLOYMENT_LIST_SORT_CRITERIA: Configuration.Settings.DeploymentListSortCriteria.DEFAULT.value,
                Configuration.Settings.Keys.DEPLOYMENT_LIST_IS_DESCENDING_ORDER: False, 
                
                Configuration.Settings.Keys.DRAFT_LIST_STYLES: None,
                Configuration.Settings.Keys.DRAFT_LIST_ADD_CARD_MODE: Configuration.Settings.DraftListAddCardMode.OFF.value,
                Configuration.Settings.Keys.DRAFT_LIST_ADD_CARD_DEPLOYMENT_DESTINATION: None,
                
                Configuration.Settings.Keys.REMOTE_SOCKET_URL: None,

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
    
    # MARK: - Generic config
    def configuration_for_key(self, key: str) -> Optional[Any]:
        return self._get_with_default_settings(key)
    
    
        

    # MARK: - User settings
    @property
    def hide_image_preview(self) -> bool:
        return self._get_with_default_settings(self.Settings.Keys.HIDE_IMAGE_PREVIEW)
    
    @property
    def image_preview_scale(self) -> float:
        return self._get_with_default_settings(self.Settings.Keys.IMAGE_PREVIEW_SCALE)
    
    @property
    def hide_deployment_cell_controls(self) -> bool:
        return self._get_with_default_settings(self.Settings.Keys.HIDE_DEPLOYMENT_CELL_CONTROLS)

    @property 
    def search_source(self) -> Settings.SearchSource:
        return self.Settings.SearchSource(self._get_with_default_settings(self.Settings.Keys.SEARCH_SOURCE))
    
    @property 
    def custom_directory_search_path(self) -> Optional[str]:
        value: Optional[str] = self._get_with_default_settings(self.Settings.Keys.CUSTOM_DIRECTORY_SEARCH_PATH)
        if value is not None and not value.isspace():
            return f'{self._get_with_default_settings(self.Settings.Keys.CUSTOM_DIRECTORY_SEARCH_PATH)}'
        return None
    
    @property
    def card_title_detail(self) -> Settings.CardTitleDetail:
        return self.Settings.CardTitleDetail(self._get_with_default_settings(self.Settings.Keys.CARD_TITLE_DETAIL))
    
    @property
    def is_deployment_list_horizontal(self) -> bool:
        return self._get_with_default_settings(self.Settings.Keys.IS_DEPLOYMENT_LIST_HORIZONTAL)
    
    @property 
    def show_resource_details(self) -> bool:
        return self._get_with_default_settings(self.Settings.Keys.SHOW_RESOURCE_DETAILS)
    
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
    def draft_list_add_card_mode(self) -> Settings.DraftListAddCardMode:
        return self._get_with_default_settings(self.Settings.Keys.DRAFT_LIST_ADD_CARD_MODE)
    
    @property
    def draft_list_add_card_deployment_destination(self) -> Optional[str]:
        return self._get_with_default_settings(self.Settings.Keys.DRAFT_LIST_ADD_CARD_DEPLOYMENT_DESTINATION)
    
    @property
    def remote_socket_url(self) -> Optional[str]:
        return self._get_with_default_settings(self.Settings.Keys.REMOTE_SOCKET_URL)

    # MARK: - Toggles
    @property
    def is_draft_list_image_preview_enabled(self) -> bool:
        return self._get_with_default_toggles(self.Toggles.Keys.DRAFT_LIST_IMAGE_PREVIEW)
    
    @property
    def is_remote_socket_connection_enabled(self) -> bool:
        return self._get_with_default_toggles(self.Toggles.Keys.REMOTE_SOCKET_CONNECTION)
    
    @property
    def is_using_legacy_deck_image_generation(self) -> bool:
        return self._get_with_default_toggles(self.Toggles.Keys.USES_LEGACY_DECK_IMAGE_GENERATION)

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
    
    # MARK: - App data
    @property
    def _app_data_dir_path(self) -> str:
        # will point to app name folder
        return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
    
    # MARK: - Config
    @property
    def _config_dir_path(self) -> str:
        # will point to app name folder
        return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
    
    @property
    def config_directory(self) -> str:
        return f'{self._config_dir_path}'
    
    @property
    def logs_dir_path(self) -> str:
        return f'{self._config_dir_path}/logs'
    
    @property
    def app_crash_log_path(self) -> str:
        return f'{self.logs_dir_path}/app_crash.log'
    
    # MARK: - Picture
    @property
    def picture_dir_path(self) -> str:
        return self._picture_dir_path
    
    @property
    def _picture_dir_path(self) -> str:
        # always points to picture dir
        # append app name
        return f'{QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation)}/{self.app_path_name}/'

    @property
    def production_dir_path(self) -> str:
        return f'{self._picture_dir_path}production/'
    
    @property
    def production_preview_dir_path(self) -> str:
        return f'{self.production_dir_path}preview/'
    
    # MARK: - Assets
    @property
    def assets_dir_path(self) -> str:
        return f'{self._app_data_dir_path}/assets/'
    
    @property
    def locally_managed_sets_dir_path(self) -> str:
        return f'{self.assets_dir_path}locally_managed_sets/'
    
    @property
    def draft_list_windows_dir_path(self) -> str:
        return f'{self.assets_dir_path}draft_list_windows/'
    
    @property
    def draft_lists_dir_path(self) -> str:
        return f'{self.assets_dir_path}draft_lists/'
    
    # MARK: - Cache
    @property
    def cache_dir_path(self) -> str:
        return f'{QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)}/'
    
    @property
    def cache_card_search_dir_path(self) -> str:
        return f'{self.cache_dir_path}card_search/' 
    
    @property
    def cache_card_search_preview_dir_path(self) -> str:
        return f'{self.cache_card_search_dir_path}preview/'
    
    @property
    def cache_history_dir_path(self) -> str:
        return f'{self.cache_dir_path}history/'
    
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
            if key not in default:
                under[key] = None
            else:
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
    
    def set_image_preview_scale(self, value: float):
        self._settings[self.Settings.Keys.IMAGE_PREVIEW_SCALE] = value
        
    def set_search_source(self, source: Configuration.Settings.SearchSource):
        self._settings[self.Settings.Keys.SEARCH_SOURCE] = source.value

    def set_custom_directory_search_path(self, value: Optional[str]):
        self._settings[self.Settings.Keys.CUSTOM_DIRECTORY_SEARCH_PATH] = value

    def set_show_resource_details(self, value: bool):
        self._settings[self.Settings.Keys.SHOW_RESOURCE_DETAILS] = value

    def set_card_title_detail(self, detail: Configuration.Settings.CardTitleDetail):
        self._settings[self.Settings.Keys.CARD_TITLE_DETAIL] = detail.value
        
    def set_is_deployment_list_horizontal(self, value: bool):
        self._settings[self.Settings.Keys.IS_DEPLOYMENT_LIST_HORIZONTAL] = value
        
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
    
    def set_draft_list_add_card_mode(self, value: Configuration.Settings.DraftListAddCardMode):
        self._settings[self.Settings.Keys.DRAFT_LIST_ADD_CARD_MODE] = value.value
    
    def set_draft_list_add_card_deployment_destination(self, value: Optional[str]):
        self._settings[self.Settings.Keys.DRAFT_LIST_ADD_CARD_DEPLOYMENT_DESTINATION] = value

    def set_remote_socket_connection_url(self, value: Optional[str]):
        self._settings[self.Settings.Keys.REMOTE_SOCKET_URL] = value
    
    def set_configuration_for_key(self, key: str, value: Any):
        self._settings[key] = value
    
    # MARK: - Toggles
    def set_is_draft_list_image_preview_enabled(self, value: bool):
        self._toggles[self.Toggles.Keys.DRAFT_LIST_IMAGE_PREVIEW] = value

    def set_is_remote_socket_connection_enabled(self, value: bool):
        self._toggles[self.Toggles.Keys.REMOTE_SOCKET_CONNECTION] = value

    def set_is_using_legacy_deck_list_image_generation(self, value: bool):
        self._toggles[self.Toggles.Keys.USES_LEGACY_DECK_IMAGE_GENERATION] = value
    
    # MARK: - Developer settings
    def set_is_mock_data(self, value: bool):
        self._settings[self.Settings.Keys.IS_MOCK_DATA] = value
        
    def set_is_delay_network_mode(self, value: bool):
        self._settings[self.Settings.Keys.IS_DELAY_NETWORK_MODE] = value