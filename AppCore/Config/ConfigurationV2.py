# Extensible

# Config.save(key: str, Val: T)

# Config.save(config_type:)
# Auto saves data
# ConfigType{ key, val }

# How to do pending changes for setting page that will only save when clicking save

# Migration strategy

from typing import Any, List

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

    def __init__(self):
        pass

    def save(self, key: str, value: Any):
        # queue up changes
        # timer
        pass

    # def save_values(self, key_value_list: List[Tuple[str, Any]]):


    def save_configuration_type(self, configuration_type: ConfigurationType):
        self.save(configuration_type.key, configuration_type.value)

    def save_configuration_type_list(self, configuration_type_list: List[ConfigurationType]):
        for i in configuration_type_list:
            self.save_configuration_type(i)

    # how do we handle temp changes that 
