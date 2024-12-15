from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QPushButton,
                             QRadioButton, QVBoxLayout, QWidget)

from AppCore.Config import Configuration

from ...AppDependencyProviding import AppDependencyProviding


class SettingsViewController(QWidget):
    def __init__(self, 
                 app_dependencies_provider: AppDependencyProviding):
        super().__init__()
        self.configuration_manager = app_dependencies_provider.configuration_manager
        self.mutable_configuration = self.configuration_manager.mutable_configuration()
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
        
        search_swudb_api_radio = QRadioButton()
        search_swudb_api_radio.setText("https://www.swu-db.com/")
        search_swudb_api_radio.toggled.connect(self.search_swudbapi_toggled)
        search_swudb_api_radio.setChecked(self.mutable_configuration.search_source == Configuration.Settings.SearchSource.SWUDBAPI)
        search_source_options_layout.addWidget(search_swudb_api_radio)
        
        search_local_radio = QRadioButton()
        search_local_radio.setText("Local")
        search_local_radio.toggled.connect(self.search_local_toggled)
        search_local_radio.setChecked(self.mutable_configuration.search_source == Configuration.Settings.SearchSource.LOCAL)
        search_source_options_layout.addWidget(search_local_radio)

        # Image Source
        image_source_row_layout = QHBoxLayout()
        image_source_row_widget = QGroupBox()
        image_source_row_widget.setLayout(image_source_row_layout)
        vertical_layout.addWidget(image_source_row_widget)
        
        image_source_label = QLabel()
        image_source_label.setText("Select image source from where images should be downloaded from:")
        image_source_row_layout.addWidget(image_source_label)
        

        image_source_options_layout = QVBoxLayout()
        image_source_options_widget = QWidget()
        image_source_options_widget.setLayout(image_source_options_layout)
        image_source_row_layout.addWidget(image_source_options_widget)
        
        image_swudb_api_radio = QRadioButton()
        image_swudb_api_radio.setText("https://www.swu-db.com/")
        image_swudb_api_radio.toggled.connect(self.image_swudbapi_toggled)
        image_swudb_api_radio.setChecked(self.mutable_configuration.image_source == Configuration.Settings.ImageSource.SWUDBAPI)
        image_source_options_layout.addWidget(image_swudb_api_radio)
        
        image_swudb_radio = QRadioButton()
        image_swudb_radio.setText("https://www.swudb.com/")
        image_swudb_radio.toggled.connect(self.image_swudb_toggled)
        image_swudb_radio.setChecked(self.mutable_configuration.image_source == Configuration.Settings.ImageSource.SWUDB)
        image_source_options_layout.addWidget(image_swudb_radio)
        
        
        
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
        
        
    def search_swudbapi_toggled(self):
        self.mutable_configuration.set_search_source(Configuration.Settings.SearchSource.SWUDBAPI)
        
    def search_local_toggled(self):
        self.mutable_configuration.set_search_source(Configuration.Settings.SearchSource.LOCAL)

    
    def image_swudbapi_toggled(self):
        self.mutable_configuration.set_image_source(Configuration.Settings.ImageSource.SWUDBAPI)
        
    def image_swudb_toggled(self):
        self.mutable_configuration.set_image_source(Configuration.Settings.ImageSource.SWUDB)


    def save_and_close(self):
        self.save_settings()
        self.close()
    
    def save_settings(self):
        self.configuration_manager.save_configuration(self.mutable_configuration)