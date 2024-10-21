import io
from pathlib import Path

import yaml

from AppCore.Config.Configuration import *
from AppCore.Observation.Events import ConfigurationUpdatedEvent
from AppCore.Observation.ObservationTower import *
from PyQt5.QtCore import QStandardPaths

class ConfigurationManager:
    def __init__(self, observation_tower: ObservationTower, configuration: Configuration):
        self._configuration = configuration
        # test = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
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


    @property
    def configuration(self) -> Configuration:
        return self._configuration
    
    @property
    def _app_config_directory(self) -> str:
        # https://doc-snapshots.qt.io/qtforpython-5.15/PySide2/QtCore/QStandardPaths.html#PySide2.QtCore.PySide2.QtCore.QStandardPaths.writableLocation
        return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation) + f'/{self.configuration.app_path_name}'
    
    @property
    def _settings_file_path(self) -> str:
        return self._app_config_directory + '/settings.yaml'

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

    def _create_directory_if_needed(self):
        my_file = Path(self._app_config_directory)
        my_file.mkdir(parents=True, exist_ok=True)

    def _write_configuration_changes(self):
        self._create_directory_if_needed()
        data = self.configuration.toJSON()
        with io.open(self._settings_file_path, 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
    


