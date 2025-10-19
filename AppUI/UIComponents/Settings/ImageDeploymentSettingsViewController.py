
from PyQt5.QtWidgets import QFileDialog

from AppCore.Config import Configuration
from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from AppUI.Configuration import MutableAppUIConfiguration
from .SettingsContainerChildProtocol import SettingsContainerChildProtocol
from R4UI import (HorizontalLabeledInputRow, Label, LineEditInt, PushButton,
                  R4UIButtonGroup, R4UICheckBox, VerticalBoxLayout,
                  VerticalGroupBox, VerticalLabeledInputRow)


class ImageDeploymentSettingsViewController(SettingsContainerChildProtocol):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        self._configuration_manager = app_dependencies_provider.configuration_manager
        self._mutable_configuration = self._configuration_manager.mutable_configuration()
        self._observation_tower = app_dependencies_provider.observation_tower
        
        self._custom_directory_search_path_label = Label(self._mutable_configuration.custom_directory_search_path if self._mutable_configuration.custom_directory_search_path is not None else "Path not set")

        VerticalBoxLayout([
            VerticalGroupBox([
                Label("Select search source from where search should be used from:"),
                R4UIButtonGroup([
                    ("https://www.starwarsunlimited.com/", Configuration.Settings.SearchSource.STARWARSUNLIMITED_FFG),
                    ("https://www.swu-db.com/", Configuration.Settings.SearchSource.SWUDBAPI),
                    ("Local Search + www.swu-db.com Images (Set 1-5) [NOTE: Will be removed]", Configuration.Settings.SearchSource.LOCAL),
                    ("Locally managed sets", Configuration.Settings.SearchSource.LOCALLY_MANAGED_DECKS)
                ], lambda x: self._mutable_configuration.set_search_source(x)) \
                .set_object_checked(self._mutable_configuration.search_source)
            ]),
            VerticalGroupBox([
                Label("Custom directory search source"),
                PushButton("Edit", self._edit_custom_dir_path),
                self._custom_directory_search_path_label
            ]),
            VerticalGroupBox([
                HorizontalLabeledInputRow("Enable resize production image", 
                                          R4UICheckBox(lambda x: self._mutable_configuration.set_resize_prod_images(x), self._mutable_configuration.resize_prod_images)),
                VerticalLabeledInputRow("Max resize length larger than 256 (will maintain aspect ratio)", 
                                        LineEditInt(self._mutable_configuration.resize_prod_images_max_size, lambda x: self._mutable_configuration.set_resize_prod_images_max_size(x)))
            ])
        ]).set_layout_to_widget(self)


    def _edit_custom_dir_path(self):
        # TODO: get from router
        directory = QFileDialog.getExistingDirectory(self, 
                                                     "Select Directory", 
                                                     self._configuration_manager.configuration.picture_dir_path)
        if directory:
            print(f"Selected directory: {directory}")
            self._mutable_configuration.set_custom_directory_search_path(directory)
            self._custom_directory_search_path_label.set_text(directory)
    
    def will_apply_settings(self, mutable_app_ui_configuration: MutableAppUIConfiguration) -> MutableAppUIConfiguration:
        mutable_app_ui_configuration.core_mutable_configuration.set_search_source(self._mutable_configuration.search_source)
        mutable_app_ui_configuration.core_mutable_configuration.set_custom_directory_search_path(self._mutable_configuration.custom_directory_search_path)
        mutable_app_ui_configuration.core_mutable_configuration.set_resize_prod_images(self._mutable_configuration.resize_prod_images)
        mutable_app_ui_configuration.core_mutable_configuration.set_resize_prod_images_max_size(self._mutable_configuration.resize_prod_images_max_size)
        return mutable_app_ui_configuration