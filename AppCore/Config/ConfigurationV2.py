import io
from pathlib import Path
from typing import Any, List, Dict

import yaml  # type: ignore

from AppCore.Service.GeneralWorker import AsyncWorker

from PySide6.QtCore import QStandardPaths
class ConfigurationType:
        def __init__(self, value: Any):
            self._value = value

        @property
        def key(self) -> str:
            raise NotImplementedError

        @property
        def value(self) -> Any:
            return self._value

class ConfigurationV2:

    # https://pydantic.dev/docs/validation/latest/get-started/

    def __init__(self):
        self._config: Dict[str, Any] = []
        self._async_worker = AsyncWorker()

    def save(self, key: str, value: Any):
        # queue up changes
        # timer
        self._config[key] = value
        self._async_worker.run(self._write_configuration_changes)

    def save_configuration_type(self, configuration_type: ConfigurationType):
        self.save(configuration_type.key, configuration_type.value)

    def save_configuration_type_list(self, configuration_type_list: List[ConfigurationType]):
        for i in configuration_type_list:
            self.save_configuration_type(i)

    def _create_directory_if_needed(self):
        my_file = Path(self._app_config_directory)
        my_file.mkdir(parents=True, exist_ok=True)

    def _write_configuration_changes(self):
        self._create_directory_if_needed()
        data = self._configuration.to_data()
        with io.open(self._settings_file_path, 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False,
                      allow_unicode=True)

    @property
    def _settings_file_path(self) -> str:
        return self._app_config_directory + '/settings_v2.yaml'

    @property
    def _app_config_directory(self) -> str:
        return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
