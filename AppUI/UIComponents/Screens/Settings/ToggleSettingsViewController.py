from AppUI.AppDependenciesProviding import AppDependenciesProviding
from AppUI.Configuration import MutableAppUIConfiguration
from AppUI.UIComponents import SettingsContainerChildProtocol
from R4UI import (HorizontalLabeledInputRow, R4UICheckBox, VerticalBoxLayout,
                  VerticalGroupBox)


class ToggleSettingsViewController(SettingsContainerChildProtocol):
    def __init__(self, app_dependencies_provider: AppDependenciesProviding):
        super().__init__()

        self._mutable_configuration = app_dependencies_provider.app_ui_configuration_manager.mutable_configuration()
        
        VerticalBoxLayout([
            VerticalGroupBox([
                HorizontalLabeledInputRow("Draft list image preview", 
                                          R4UICheckBox(lambda x: self._mutable_configuration.core_mutable_configuration.set_is_draft_list_image_preview_enabled(x), self._mutable_configuration.core_configuration.is_draft_list_image_preview_enabled)),
            ])
        ]).set_layout_to_widget(self)
        
    def will_apply_settings(self, mutable_app_ui_configuration: MutableAppUIConfiguration) -> MutableAppUIConfiguration:
        mutable_app_ui_configuration.core_mutable_configuration.set_is_draft_list_image_preview_enabled(self._mutable_configuration.core_configuration.is_draft_list_image_preview_enabled)
        return mutable_app_ui_configuration