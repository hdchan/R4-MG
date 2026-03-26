from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from AppUI.Configuration import MutableAppUIConfiguration
from .SettingsContainerChildProtocol import SettingsContainerChildProtocol
from R4UI import (HorizontalLabeledInputRow, RCheckBox, VerticalBoxLayout,
                  VerticalGroupBox, LineEditText, RVerticallyExpandingSpacer)


class ToggleSettingsViewController(SettingsContainerChildProtocol):
    def __init__(self, app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()

        self._mutable_configuration = app_dependencies_provider.app_ui_configuration_manager.mutable_configuration()
        # self._mutable_core_configuration = self._mutable_configuration.core_mutable_configuration
        
        VerticalBoxLayout([
            VerticalGroupBox([
                HorizontalLabeledInputRow("Launch draft list image preview on startup", 
                                          RCheckBox(lambda x: self._mutable_configuration.core_mutable_configuration.set_is_draft_list_image_preview_enabled(x), self._mutable_configuration.core_configuration.is_draft_list_image_preview_enabled)),
               
                HorizontalLabeledInputRow("Use legacy deck list image generator", 
                                          RCheckBox(lambda x: self._mutable_configuration.core_mutable_configuration.set_is_using_legacy_deck_list_image_generation(x), self._mutable_configuration.core_configuration.is_using_legacy_deck_image_generation)),
                HorizontalLabeledInputRow("Use SQLite for managed set search", 
                                          RCheckBox(lambda x: self._mutable_configuration.core_mutable_configuration.set_is_using_sqlite_search_for_managed_set_search(x), self._mutable_configuration.core_configuration.is_using_sqlite_search_for_managed_set_search))
            ])
        ]).set_layout_to_widget(self).add_spacer(RVerticallyExpandingSpacer())

    def will_apply_settings(self, mutable_app_ui_configuration: MutableAppUIConfiguration) -> MutableAppUIConfiguration:
        mutable_app_ui_configuration.core_mutable_configuration.set_is_draft_list_image_preview_enabled(self._mutable_configuration.core_configuration.is_draft_list_image_preview_enabled)

        mutable_app_ui_configuration.core_mutable_configuration.set_is_using_legacy_deck_list_image_generation(self._mutable_configuration.core_configuration.is_using_legacy_deck_image_generation)
        mutable_app_ui_configuration.core_mutable_configuration.set_is_using_sqlite_search_for_managed_set_search(self._mutable_configuration.core_configuration.is_using_sqlite_search_for_managed_set_search)

        return mutable_app_ui_configuration