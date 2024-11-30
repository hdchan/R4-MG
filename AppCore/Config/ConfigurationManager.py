import io
from copy import deepcopy
from pathlib import Path

import yaml

from AppCore.Config.Configuration import *
from AppCore.Observation.Events import ConfigurationUpdatedEvent
from AppCore.Observation.ObservationTower import *


class MutableConfiguration(Configuration):
    def set_hide_image_preview(self, value: bool):
        self._settings.hide_image_preview = value
        
    def set_is_mock_data(self, value: bool):
        self._settings.is_mock_data = value
        
    def set_is_delay_network_mode(self, value: bool):
        self._settings.is_delay_network_mode = value
        
    def set_image_source(self, source: Configuration.Settings.ImageSource):
        self._settings.image_source = source

    def set_show_resource_details(self, value: bool):
        self._settings.show_resource_details = value

class ConfigurationManager(ConfigurationProvider):
    def __init__(self, observation_tower: ObservationTower):
        self._configuration = MutableConfiguration()
        
        self._create_directory_if_needed()
        my_file = Path(self._settings_file_path)
        if not my_file.is_file():
            with open(self._settings_file_path, 'w+') as stream:
                yaml.safe_load(stream)
        with open(self._settings_file_path, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            if data_loaded is not None:
                self._configuration.loadJSON(data_loaded)
        self.observation_tower = observation_tower
        
        self._real_configuration = deepcopy(self._configuration)

    @property
    def configuration(self) -> Configuration:
        return self._real_configuration
    
    
    @property
    def _app_config_directory(self) -> str:
        return self._configuration.config_directory
    
    @property
    def _settings_file_path(self) -> str:
        return self._app_config_directory + '/settings.yaml'
    
    
    def discard(self):
        self._configuration = deepcopy(self._real_configuration)

    def save(self):
        self._real_configuration = self._configuration
        self._configuration = deepcopy(self._real_configuration)
        self._notify_configuration_changed()

    def toggle_hide_image_preview(self, is_on: bool) -> 'ConfigurationManager':
        self._configuration.set_hide_image_preview(is_on)
        return self
    
    def toggle_show_resource_details(self, is_on: bool) -> 'ConfigurationManager':
        self._configuration.set_show_resource_details(is_on)
        return self

    def toggle_mock_data_mode(self, is_on: bool) -> 'ConfigurationManager':
        self._configuration.set_is_mock_data(is_on)
        return self
        
    def toggle_delay_network_mode(self, is_on: bool) -> 'ConfigurationManager':
        self._configuration.set_is_delay_network_mode(is_on)
        return self

    def toggle_popout_production_images_mode(self, is_on: bool) -> 'ConfigurationManager':
        self._configuration.is_popout_production_images_mode = is_on
        return self
    
    def set_image_source(self, source: Configuration.Settings.ImageSource):
        self._configuration.set_image_source(source)
    
    def toggle_image_source(self, is_on: bool) -> 'ConfigurationManager':
        if is_on:
            self._configuration.set_image_source(Configuration.Settings.ImageSource.SWUDB)
        else:
            self._configuration.set_image_source(Configuration.Settings.ImageSource.SWUDBAPI)
        return self

    def _notify_configuration_changed(self):
        self.observation_tower.notify(ConfigurationUpdatedEvent(self.configuration))
        self._write_configuration_changes()

    def _create_directory_if_needed(self):
        my_file = Path(self._app_config_directory)
        my_file.mkdir(parents=True, exist_ok=True)

    def _write_configuration_changes(self):
        self._create_directory_if_needed()
        data = self._real_configuration.toJSON()
        with io.open(self._settings_file_path, 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
    


