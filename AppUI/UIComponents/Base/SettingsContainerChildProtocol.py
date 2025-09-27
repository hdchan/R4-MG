from typing import Optional

from AppUI.Configuration import MutableAppUIConfiguration


class SettingsContainerChildProtocol:
    def will_apply_settings(self, mutable_app_ui_configuration: MutableAppUIConfiguration) -> MutableAppUIConfiguration:
        raise Exception