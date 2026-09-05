import io
from pathlib import Path
from typing import Any, List, Dict
import json
import yaml  # type: ignore
# from AppCore.Utilities.Debouncer import Debouncer
# from AppCore.Service.GeneralWorker import AsyncWorker

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

    def to_dict(self) -> Dict[str, Any]:
        return { self.key, self.value }

class ConfigurationV2:
    # https://pydantic.dev/docs/validation/latest/get-started/

    def __init__(self, file_path: str):
        self._file_path = file_path
        self._config: Dict[str, Any] = {}

        self._create_directory_if_needed()

        try:
            with open(self._file_path, 'r') as stream:
                data_loaded = yaml.safe_load(stream)
                self._config = data_loaded
                print(data_loaded)
        except Exception:
            with open(self._file_path, 'w+') as stream:
                print("file did not exist, creating")

    def save(self, kvp: Dict[str, Any]):
        self._config = self._config | kvp
        self._write_configuration_changes()

    def save_configuration_type_list(self, configuration_type_list: List[ConfigurationType]):
        result = {i.key: i.value for idx, i in enumerate(configuration_type_list)}
        self.save(result)

    def _create_directory_if_needed(self):
        Path(self._file_path).parent.mkdir(parents=True, exist_ok=True)

    def _write_configuration_changes(self):
        self._create_directory_if_needed()
        data = self._config
        with io.open(self._file_path, 'w', encoding='utf8') as outfile:
            yaml.dump(data,
                      outfile,
                      default_flow_style=False,
                      allow_unicode=True)

class Test(ConfigurationType):
    def __init__(self, value: int):
        super().__init__(value)

    @property
    def key(self) -> str:
        return "a"

class Test2(ConfigurationType):
    def __init__(self, value: int):
        super().__init__(value)

    @property
    def key(self) -> str:
        return "b"

config = ConfigurationV2(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation) + '/settings_v2.yaml')
config.save_configuration_type_list([Test(2), Test2(2)])
