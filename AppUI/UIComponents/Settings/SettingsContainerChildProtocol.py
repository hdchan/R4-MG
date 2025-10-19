from AppUI.Configuration import MutableAppUIConfiguration
from R4UI import RWidget

class SettingsContainerChildProtocol(RWidget):
    def will_apply_settings(self, mutable_app_ui_configuration: MutableAppUIConfiguration) -> MutableAppUIConfiguration:
        raise Exception