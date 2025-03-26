from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (QCheckBox, QGroupBox, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QRadioButton, QVBoxLayout,
                             QWidget)

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
        
        search_ffg_radio = QRadioButton()
        search_ffg_radio.setText("https://www.starwarsunlimited.com/")
        search_ffg_radio.toggled.connect(self.search_ffg_toggled)
        search_ffg_radio.setChecked(self.mutable_configuration.search_source == Configuration.Settings.SearchSource.STARWARSUNLIMITED_FFG)
        search_source_options_layout.addWidget(search_ffg_radio)
        
        search_swudb_api_radio = QRadioButton()
        search_swudb_api_radio.setText("https://www.swu-db.com/")
        search_swudb_api_radio.toggled.connect(self.search_swudbapi_toggled)
        search_swudb_api_radio.setChecked(self.mutable_configuration.search_source == Configuration.Settings.SearchSource.SWUDBAPI)
        search_source_options_layout.addWidget(search_swudb_api_radio)
        
        search_local_radio = QRadioButton()
        search_local_radio.setText("Local Search + www.swu-db.com Images (Set 1-4)")
        search_local_radio.toggled.connect(self.search_local_toggled)
        search_local_radio.setChecked(self.mutable_configuration.search_source == Configuration.Settings.SearchSource.LOCAL)
        search_source_options_layout.addWidget(search_local_radio)

        # Image Source
        # image_source_row_layout = QHBoxLayout()
        # image_source_row_widget = QGroupBox()
        # image_source_row_widget.setLayout(image_source_row_layout)
        # vertical_layout.addWidget(image_source_row_widget)
        
        # image_source_label = QLabel()
        # image_source_label.setText("Select image source from where images should be downloaded from:")
        # image_source_row_layout.addWidget(image_source_label)
        

        # image_source_options_layout = QVBoxLayout()
        # image_source_options_widget = QWidget()
        # image_source_options_widget.setLayout(image_source_options_layout)
        # image_source_row_layout.addWidget(image_source_options_widget)
        
        # image_swudb_api_radio = QRadioButton()
        # image_swudb_api_radio.setText("https://www.swu-db.com/")
        # image_swudb_api_radio.toggled.connect(self.image_swudbapi_toggled)
        # image_swudb_api_radio.setChecked(self.mutable_configuration.image_source == Configuration.Settings.ImageSource.SWUDBAPI)
        # image_source_options_layout.addWidget(image_swudb_api_radio)
        
        # image_swudb_radio = QRadioButton()
        # image_swudb_radio.setText("https://www.swudb.com/")
        # image_swudb_radio.toggled.connect(self.image_swudb_toggled)
        # image_swudb_radio.setChecked(self.mutable_configuration.image_source == Configuration.Settings.ImageSource.SWUDB)
        # image_source_options_layout.addWidget(image_swudb_radio)
        
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
        enable_resize_prod_image_row_checkbox.setChecked(self.mutable_configuration.resize_prod_images)
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
        max_resize_prod_image_size_input.setText(str(self.mutable_configuration.resize_prod_images_max_size))
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
        
    def search_ffg_toggled(self):
        self.mutable_configuration.set_search_source(Configuration.Settings.SearchSource.STARWARSUNLIMITED_FFG)
        
    def search_swudbapi_toggled(self):
        self.mutable_configuration.set_search_source(Configuration.Settings.SearchSource.SWUDBAPI)
        
    def search_local_toggled(self):
        self.mutable_configuration.set_search_source(Configuration.Settings.SearchSource.LOCAL)

    
    def image_swudbapi_toggled(self):
        self.mutable_configuration.set_image_source(Configuration.Settings.ImageSource.SWUDBAPI)
        
    def image_swudb_toggled(self):
        self.mutable_configuration.set_image_source(Configuration.Settings.ImageSource.SWUDB)

    def enable_resize_prod_image(self, state: Qt.CheckState):
        if state == Qt.CheckState.Checked:
            self.mutable_configuration.set_resize_prod_images(True)
        else:
            self.mutable_configuration.set_resize_prod_images(False)
            
    def max_resize_prod_image_size_updated(self, text: str):
        # TODO: guard against invalid value
        try:
            self.mutable_configuration.set_resize_prod_images_max_size(int(text))
        except:
            pass


    def save_and_close(self):
        self.save_settings()
        self.close()
    
    def save_settings(self):
        self.configuration_manager.save_configuration(self.mutable_configuration)