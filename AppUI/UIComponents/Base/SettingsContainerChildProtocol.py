from AppUI.Configuration import MutableAppUIConfiguration
from R4UI import R4UIWidget

class SettingsContainerChildProtocol(R4UIWidget):
    def will_apply_settings(self, mutable_app_ui_configuration: MutableAppUIConfiguration) -> MutableAppUIConfiguration:
        raise Exception