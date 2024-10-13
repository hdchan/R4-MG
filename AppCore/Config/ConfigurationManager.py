from AppCore.Observation.Events import ConfigurationUpdatedEvent
from AppCore.Config.Configuration import *
from AppCore.Observation.ObservationTower import *
import yaml
import io
from pathlib import Path

SETTINGS_FILE_NAME = 'settings.yaml'

class ConfigurationManager:
    def __init__(self, observation_tower: ObservationTower):
        self._configuration = Configuration()
        my_file = Path(SETTINGS_FILE_NAME)
        if not my_file.is_file():
            with open(SETTINGS_FILE_NAME, 'w+') as stream:
                yaml.safe_load(stream)
        with open(SETTINGS_FILE_NAME, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            if data_loaded is not None:
                self._configuration.loadJSON(data_loaded)
        self.observation_tower = observation_tower

    @property
    def configuration(self) -> Configuration:
        return self._configuration

    def toggle_performance_mode(self, is_on: bool):
        self.configuration.is_performance_mode = is_on
        self._notify_configuration_changed()

    def toggle_mock_data_mode(self, is_on: bool):
        self.configuration.is_mock_data = is_on
        self._notify_configuration_changed()
        
    def toggle_delay_network_mode(self, is_on: bool):
        self.configuration.is_delay_network_mode = is_on
        self._notify_configuration_changed()

    def _notify_configuration_changed(self):
        event = ConfigurationUpdatedEvent(configuration=self.configuration)
        self.observation_tower.notify(event)
        self._write_configuration_changes()

    def _write_configuration_changes(self):
        data = self.configuration.toJSON()
        with io.open(SETTINGS_FILE_NAME, 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
    


