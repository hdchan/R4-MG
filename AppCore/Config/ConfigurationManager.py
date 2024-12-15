import io
from copy import deepcopy
from pathlib import Path

import yaml

from AppCore.Config.Configuration import *
from AppCore.Observation.Events import (ApplicationEvent,
                                        ConfigurationUpdatedEvent)
from AppCore.Observation.ObservationTower import *

# from PyQt5.QtCore import QTimer


class ConfigurationManager(TransmissionReceiverProtocol):
    def __init__(self, observation_tower: ObservationTower):
        self._configuration = MutableConfiguration.default()
        self.observation_tower = observation_tower

        self._create_directory_if_needed()
        my_file = Path(self._settings_file_path)
        if not my_file.is_file():
            with open(self._settings_file_path, 'w+') as stream:
                yaml.safe_load(stream)
        with open(self._settings_file_path, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            if data_loaded is not None:
                self._configuration = MutableConfiguration(data_loaded)

        # self._save_async_timer = QTimer()
        # self._save_async_timer.setSingleShot(True)
        # self._save_async_timer.timeout.connect(self.save)
        # self.debounce_time = 5000

        observation_tower.subscribe(self, ApplicationEvent)

    @property
    def configuration(self) -> Configuration:
        return deepcopy(self._configuration)
    
    def mutable_configuration(self) -> MutableConfiguration:
        return deepcopy(self._configuration)

    @property
    def _app_config_directory(self) -> str:
        return self._configuration.config_directory
    
    @property
    def _settings_file_path(self) -> str:
        return self._app_config_directory + '/settings.yaml'
    
    def save_configuration(self, new_configuration: MutableConfiguration):
        print('saving configuration')
        old_configuration = deepcopy(self._configuration)
        self._configuration = new_configuration
        self._notify_configuration_changed(old_configuration)

    # def save_async(self):
    #     # TODO: prevent notifications for async save?
    #     self._save_async_timer.start(self.debounce_time)
    

    def _notify_configuration_changed(self, old_configuration: Configuration):
        self.observation_tower.notify(ConfigurationUpdatedEvent(self.configuration, old_configuration))
        self._write_configuration_changes()

    def _create_directory_if_needed(self):
        my_file = Path(self._app_config_directory)
        my_file.mkdir(parents=True, exist_ok=True)

    def _write_configuration_changes(self):
        self._create_directory_if_needed()
        data = self._configuration.to_data()
        with io.open(self._settings_file_path, 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
    
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == ApplicationEvent:
            if event.event_type == ApplicationEvent.EventType.APP_WILL_TERMINATE:
                # self.save(notify=False)
                pass