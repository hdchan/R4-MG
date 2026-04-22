import io
from copy import deepcopy
from pathlib import Path

import yaml  # type: ignore

from AppCore.Config.Configuration import Configuration, MutableConfiguration
from AppCore.Observation.Events import (ApplicationEvent,
                                        ConfigurationUpdatedEvent)
from AppCore.Observation.ObservationTower import (ObservationTower,
                                                  TransmissionProtocol,
                                                  TransmissionReceiverProtocol)
from AppCore.Service.GeneralWorker import AsyncWorker


class ConfigurationManager(TransmissionReceiverProtocol):
    def __init__(self,
                 observation_tower: ObservationTower):
        self._configuration = MutableConfiguration.default()
        # ensure that the app path points to our designated application name
        assert (
            Path(self._configuration.config_directory).parts[-1] == Configuration.APP_NAME)
        self._observation_tower = observation_tower
        self._async_worker = AsyncWorker()

        self._create_directory_if_needed()
        my_file = Path(self._settings_file_path)
        if not my_file.is_file():
            with open(self._settings_file_path, 'w+') as stream:
                yaml.safe_load(stream)
        with open(self._settings_file_path, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            if data_loaded is not None:
                self._configuration = MutableConfiguration(data_loaded)

        self._observation_tower.subscribe_multi(self, [ApplicationEvent])

    @property
    def configuration(self) -> Configuration:
        return self.mutable_configuration()

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
        self._observation_tower.notify(ConfigurationUpdatedEvent(
            self.configuration, old_configuration))
        self._async_worker.run(self._write_configuration_changes)

    def _create_directory_if_needed(self):
        my_file = Path(self._app_config_directory)
        my_file.mkdir(parents=True, exist_ok=True)

    def _write_configuration_changes(self):
        self._create_directory_if_needed()
        data = self._configuration.to_data()
        with io.open(self._settings_file_path, 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False,
                      allow_unicode=True)

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is ApplicationEvent:
            if event.event_type == ApplicationEvent.EventType.APP_WILL_TERMINATE:
                # self.save(notify=False)
                pass
