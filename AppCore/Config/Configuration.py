from typing import Any, Dict

PRODUCTION_FILE_PATH = './production/'
PRODUCTION_PREVIEW_FILE_PATH = PRODUCTION_FILE_PATH + 'preview/'
CACHE_FILE_PATH = './cache/'
CACHE_PREVIEW_FILE_PATH = CACHE_FILE_PATH + 'preview/'

class Configuration:
    class Toggles:
        def __init__(self):
            self.developer_mode = False
            
    class Settings:
        def __init__(self):
            self.is_performance_mode = False
            self.production_file_path = PRODUCTION_FILE_PATH
            self.production_preview_file_path = PRODUCTION_PREVIEW_FILE_PATH
            self.cache_file_path = CACHE_FILE_PATH
            self.cache_preview_file_path = CACHE_PREVIEW_FILE_PATH
            
            self.is_mock_data = False
            self.is_delay_network_mode = False
            # self.network_delay_duration = 0

    def __init__(self):
        self._app_display_name = 'R4-MG'
        self._app_ui_version = '0.2.0'
        self._app_core_version = '0.2.0'

        self._toggles = Configuration.Toggles()
        self._settings = Configuration.Settings()

    @property
    def app_display_name(self):
        if self.is_developer_mode:
            return self._app_display_name + " [DEVELOPER MODE]"
        else:
            return self._app_display_name

    @property
    def app_ui_version(self):
        return self._app_ui_version
    
    @property
    def is_performance_mode(self) -> bool:
        return self._settings.is_performance_mode
    
    @is_performance_mode.setter
    def is_performance_mode(self, value: bool):
        self._settings.is_performance_mode = value
        
    @property
    def production_file_path(self) -> str:
        return self._settings.production_file_path
    
    @property
    def production_preview_file_path(self) -> str:
        return self._settings.production_preview_file_path
    
    @property
    def cache_file_path(self) -> str:
        return self._settings.cache_file_path
    
    @property
    def cache_preview_file_path(self) -> str:
        return self._settings.cache_preview_file_path

    # MARK: - Developer settings

    @property
    def is_developer_mode(self) -> bool:
        return self._toggles.developer_mode

    @property
    def is_mock_data(self) -> bool:
        if self.is_developer_mode:
            return self._settings.is_mock_data
        else:
            return False
    
    @is_mock_data.setter
    def is_mock_data(self, value: bool):
        self._settings.is_mock_data = value
        
    @property
    def is_delay_network_mode(self) -> bool:
        if self.is_developer_mode:
            return self._settings.is_delay_network_mode
        else:
            return False
        
    @is_delay_network_mode.setter
    def is_delay_network_mode(self, value: bool):
        self._settings.is_delay_network_mode = value
        
    @property
    def network_delay_duration(self) -> int:
        if self.is_delay_network_mode:
            return 5
        else:
            return 0
        

    def loadJSON(self, json: Dict[str, Any]):
        toggles = json.get('toggles', {})
        if toggles is None:
            toggles = {}
        settings = json.get('settings', {})
        if settings is None:
            settings = {}
        
        self._settings.is_performance_mode = settings.get('is_performance_mode', False) # type: ignore
        
        self._toggles.developer_mode = toggles.get('developer_mode', False) # type: ignore
        self._settings.is_mock_data = settings.get('is_mock_data', False) # type: ignore
        self._settings.is_delay_network_mode = settings.get('is_delay_network_mode', False) # type: ignore
        

    def toJSON(self) -> Dict[str, object]:
        config: Dict[str, object] = {
            "toggles": {
            },
            "settings": {
                "is_performance_mode": self.is_performance_mode
            }
        }
        if self._toggles.developer_mode:
            config['toggles']['developer_mode'] = self._toggles.developer_mode # type: ignore
            config['settings']['is_mock_data'] = self._settings.is_mock_data # type: ignore
            config['settings']['is_delay_network_mode'] = self._settings.is_delay_network_mode # type: ignore
        return config

