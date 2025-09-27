from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (QCheckBox, QGroupBox, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QRadioButton, QVBoxLayout,
                             QWidget, QFileDialog)

from AppCore.Config import Configuration
from AppUI.AppDependenciesProviding import AppDependenciesProviding
from AppUI.UIComponents import SettingsContainerChildProtocol
from AppUI.Configuration import MutableAppUIConfiguration
class SettingsViewController(QWidget, SettingsContainerChildProtocol):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesProviding):
        super().__init__()
        self._configuration_manager = app_dependencies_provider.configuration_manager
        self._mutable_configuration = self._configuration_manager.mutable_configuration()
        self._observation_tower = app_dependencies_provider.observation_tower
        
        self.setWindowTitle("Settings")

        vertical_layout = QVBoxLayout()
        self.setLayout(vertical_layout)


        # Image Source
        search_source_row_layout = QHBoxLayout()
        search_source_row_widget = QGroupBox()
        search_source_row_widget.setLayout(search_source_row_layout)
        vertical_layout.addWidget(search_source_row_widget)
        
        search_source_label = QLabel()
        search_source_label.setText("Select search source from where search should be used from:")
        search_source_row_layout.addWidget(search_source_label)
        

        search_source_options_layout = QVBoxLayout()
        search_source_options_widget = QWidget()
        search_source_options_widget.setLayout(search_source_options_layout)
        search_source_row_layout.addWidget(search_source_options_widget)
        
        search_ffg_radio = QRadioButton()
        search_ffg_radio.setText("https://www.starwarsunlimited.com/")
        search_ffg_radio.toggled.connect(self.search_ffg_toggled)
        search_ffg_radio.setChecked(self._mutable_configuration.search_source == Configuration.Settings.SearchSource.STARWARSUNLIMITED_FFG)
        search_source_options_layout.addWidget(search_ffg_radio)
        
        search_swudb_api_radio = QRadioButton()
        search_swudb_api_radio.setText("https://www.swu-db.com/")
        search_swudb_api_radio.toggled.connect(self.search_swudbapi_toggled)
        search_swudb_api_radio.setChecked(self._mutable_configuration.search_source == Configuration.Settings.SearchSource.SWUDBAPI)
        search_source_options_layout.addWidget(search_swudb_api_radio)
        
        # TODO: deprecate 
        search_local_radio = QRadioButton()
        search_local_radio.setText("Local Search + www.swu-db.com Images (Set 1-5) [NOTE: Will be removed]")
        search_local_radio.toggled.connect(self.search_local_toggled)
        search_local_radio.setChecked(self._mutable_configuration.search_source == Configuration.Settings.SearchSource.LOCAL)
        search_source_options_layout.addWidget(search_local_radio)
        
        search_locally_managed_decks_radio = QRadioButton()
        search_locally_managed_decks_radio.setText("Locally managed sets")
        search_locally_managed_decks_radio.toggled.connect(self.search_locally_managed_decks_toggled)
        search_locally_managed_decks_radio.setChecked(self._mutable_configuration.search_source == Configuration.Settings.SearchSource.LOCALLY_MANAGED_DECKS)
        search_source_options_layout.addWidget(search_locally_managed_decks_radio)
        
        # Custom Directory Search
        custom_directory_search_source_row_layout = QVBoxLayout()
        custom_directory_search_source_row_widget = QGroupBox()
        custom_directory_search_source_row_widget.setLayout(custom_directory_search_source_row_layout)
        vertical_layout.addWidget(custom_directory_search_source_row_widget)
        
        custom_directory_search_source_label = QLabel()
        custom_directory_search_source_label.setText("Custom directory search source")
        custom_directory_search_source_row_layout.addWidget(custom_directory_search_source_label)
        
        custom_directory_search_source_options_layout = QHBoxLayout()
        custom_directory_search_source_options_widget = QWidget()
        custom_directory_search_source_options_widget.setLayout(custom_directory_search_source_options_layout)
        custom_directory_search_source_row_layout.addWidget(custom_directory_search_source_options_widget)
        
        custom_directory_search_source_button = QPushButton()
        custom_directory_search_source_button.setText("Edit")
        custom_directory_search_source_button.clicked.connect(self._edit_custom_dir_path)
        custom_directory_search_source_options_layout.addWidget(custom_directory_search_source_button)
        
        self._custom_directory_search_source_value_label = QLabel()
        custom_directory_search_source_options_layout.addWidget(self._custom_directory_search_source_value_label, 2)
        
        # Production Image Resizing
        resize_prod_image_row_layout = QHBoxLayout()
        resize_prod_image_row_widget = QGroupBox()
        resize_prod_image_row_widget.setLayout(resize_prod_image_row_layout)
        vertical_layout.addWidget(resize_prod_image_row_widget)
        
        resize_prod_image_options_layout = QVBoxLayout()
        resize_prod_image_options_widget = QWidget()
        resize_prod_image_options_widget.setLayout(resize_prod_image_options_layout)
        resize_prod_image_row_layout.addWidget(resize_prod_image_options_widget)
        
        
        enable_resize_prod_image_row_layout = QHBoxLayout()
        enable_resize_prod_image_row_widget = QWidget()
        enable_resize_prod_image_row_widget.setLayout(enable_resize_prod_image_row_layout)
        resize_prod_image_options_layout.addWidget(enable_resize_prod_image_row_widget)
        
        enable_resize_prod_image_label = QLabel()
        enable_resize_prod_image_label.setText("Enable resize production image")
        enable_resize_prod_image_row_layout.addWidget(enable_resize_prod_image_label)
        
        enable_resize_prod_image_row_checkbox = QCheckBox()
        enable_resize_prod_image_row_checkbox.setChecked(self._mutable_configuration.resize_prod_images)
        enable_resize_prod_image_row_checkbox.stateChanged.connect(self.enable_resize_prod_image)
        enable_resize_prod_image_row_layout.addWidget(enable_resize_prod_image_row_checkbox)
        
        
        max_resize_prod_image_size_row_layout = QHBoxLayout()
        max_resize_prod_image_size_row_widget = QWidget()
        max_resize_prod_image_size_row_widget.setLayout(max_resize_prod_image_size_row_layout)
        resize_prod_image_options_layout.addWidget(max_resize_prod_image_size_row_widget)
        
        max_resize_prod_image_size_label = QLabel()
        max_resize_prod_image_size_label.setText("Max resize length (will maintain aspect ratio)")
        max_resize_prod_image_size_row_layout.addWidget(max_resize_prod_image_size_label)
        
        max_resize_prod_image_size_input = QLineEdit()
        max_resize_prod_image_size_input.setPlaceholderText("greater than or equal to 256")
        max_resize_prod_image_size_input.setValidator(QIntValidator(256, 2000, max_resize_prod_image_size_input))
        max_resize_prod_image_size_input.setText(str(self._mutable_configuration.resize_prod_images_max_size))
        max_resize_prod_image_size_input.textChanged.connect(self.max_resize_prod_image_size_updated)
        max_resize_prod_image_size_row_layout.addWidget(max_resize_prod_image_size_input)
        
        # Bottom buttons
        buttons_layout = QHBoxLayout()
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        vertical_layout.addWidget(buttons_widget)
        
        apply_button = QPushButton()
        apply_button.setText("Apply")
        apply_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(apply_button)
        
        save_and_close = QPushButton()
        save_and_close.setText("Save && Close")
        save_and_close.clicked.connect(self.save_and_close)
        buttons_layout.addWidget(save_and_close)

        self._sync_ui()

    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration

    def _sync_ui(self):
        path_text = "Path not set"
        if self._configuration_manager.configuration.custom_directory_search_path is not None:
            path_text = self._configuration_manager.configuration.custom_directory_search_path
        self._custom_directory_search_source_value_label.setText(path_text)

    def _edit_custom_dir_path(self):
        directory = QFileDialog.getExistingDirectory(self, 
                                                     "Select Directory", 
                                                     self._configuration_manager.configuration.picture_dir_path)
        if directory:
            print(f"Selected directory: {directory}")
            self._mutable_configuration.set_custom_directory_search_path(directory)
            self._custom_directory_search_source_value_label.setText(self._mutable_configuration.custom_directory_search_path)
    
    def search_ffg_toggled(self):
        self._mutable_configuration.set_search_source(Configuration.Settings.SearchSource.STARWARSUNLIMITED_FFG)
        
    def search_swudbapi_toggled(self):
        self._mutable_configuration.set_search_source(Configuration.Settings.SearchSource.SWUDBAPI)
        
    def search_local_toggled(self):
        self._mutable_configuration.set_search_source(Configuration.Settings.SearchSource.LOCAL)
        
    def search_locally_managed_decks_toggled(self):
        self._mutable_configuration.set_search_source(Configuration.Settings.SearchSource.LOCALLY_MANAGED_DECKS)

    def enable_resize_prod_image(self, state: Qt.CheckState):
        if state == Qt.CheckState.Checked:
            self._mutable_configuration.set_resize_prod_images(True)
        else:
            self._mutable_configuration.set_resize_prod_images(False)
            
    def max_resize_prod_image_size_updated(self, text: str):
        # TODO: guard against invalid value
        try:
            self._mutable_configuration.set_resize_prod_images_max_size(int(text))
        except:
            pass


    def save_and_close(self):
        self.save_settings()
        self.close()
    
    def save_settings(self):
        self._configuration_manager.save_configuration(self._mutable_configuration)
    
    def will_apply_settings(self, mutable_app_ui_configuration: MutableAppUIConfiguration) -> MutableAppUIConfiguration:
        mutable_app_ui_configuration.core_mutable_configuration.set_search_source(self._mutable_configuration.search_source)
        return mutable_app_ui_configuration