from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from AppUI.Configuration import MutableAppUIConfiguration
from .SettingsContainerChildProtocol import SettingsContainerChildProtocol
from R4UI import (HorizontalLabeledInputRow, R4UICheckBox, VerticalBoxLayout,
                  VerticalGroupBox, LineEditText, R4UIVerticallyExpandingSpacer)


class ToggleSettingsViewController(SettingsContainerChildProtocol):
    def __init__(self, app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()

        self._mutable_configuration = app_dependencies_provider.app_ui_configuration_manager.mutable_configuration()
        # self._mutable_core_configuration = self._mutable_configuration.core_mutable_configuration
        
        VerticalBoxLayout([
            VerticalGroupBox([
                HorizontalLabeledInputRow("Launch draft list image preview on startup", 
                                          R4UICheckBox(lambda x: self._mutable_configuration.core_mutable_configuration.set_is_draft_list_image_preview_enabled(x), self._mutable_configuration.core_configuration.is_draft_list_image_preview_enabled)),
                HorizontalLabeledInputRow("Enable remote socket connection feature", 
                                          R4UICheckBox(lambda x: self._mutable_configuration.core_mutable_configuration.set_is_remote_socket_connection_enabled(x), self._mutable_configuration.core_configuration.is_remote_socket_connection_enabled)),
                HorizontalLabeledInputRow("Remote socket connection URL", 
                                          LineEditText(self._mutable_configuration.core_configuration.remote_socket_url, self._mutable_configuration.core_mutable_configuration.set_remote_socket_connection_url))
            ])
        ]).set_layout_to_widget(self).add_spacer(R4UIVerticallyExpandingSpacer())

    def will_apply_settings(self, mutable_app_ui_configuration: MutableAppUIConfiguration) -> MutableAppUIConfiguration:
        mutable_app_ui_configuration.core_mutable_configuration.set_is_draft_list_image_preview_enabled(self._mutable_configuration.core_configuration.is_draft_list_image_preview_enabled)

        mutable_app_ui_configuration.core_mutable_configuration.set_is_remote_socket_connection_enabled(self._mutable_configuration.core_configuration.is_remote_socket_connection_enabled)
        mutable_app_ui_configuration.core_mutable_configuration.set_remote_socket_connection_url(self._mutable_configuration.core_configuration.remote_socket_url)

        return mutable_app_ui_configuration