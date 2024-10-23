from PyQt5.QtWidgets import (QCheckBox, QHBoxLayout, QLabel, QRadioButton,
                             QVBoxLayout, QWidget, QPushButton)

from AppCore.Config import Configuration, ConfigurationManager


class SettingsViewController(QWidget):
    def __init__(self, configuration_manager: ConfigurationManager):
        super().__init__()
        self.configuration_manager = configuration_manager
        self.configuration_manager.discard()
        configuration = configuration_manager.configuration
        self.setWindowTitle("Settings")
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        checkbox = QCheckBox("Performance mode: hides preview images to reduce application memory")
        checkbox.stateChanged.connect(self.state_changed)
        checkbox.setChecked(configuration.is_performance_mode)
        layout.addWidget(checkbox)
        
        source_label = QLabel()
        source_label.setText("Select image source from where images should be downloaded from:")
        
        layout.addWidget(source_label)
        
        h_layout = QHBoxLayout()
        h_widget = QWidget()
        h_widget.setLayout(h_layout)
        
        
        
        swudb_api_radio = QRadioButton()
        swudb_api_radio.setText("https://www.swu-db.com/")
        swudb_api_radio.toggled.connect(self.swudbapi_toggled)
        swudb_api_radio.setChecked(configuration.image_source.value == 0)
        h_layout.addWidget(swudb_api_radio)
        
        swudb_radio = QRadioButton()
        swudb_radio.setText("https://www.swudb.com/")
        swudb_radio.toggled.connect(self.swudb_toggled)
        swudb_radio.setChecked(configuration.image_source.value == 1)
        h_layout.addWidget(swudb_radio)
        
        layout.addWidget(h_widget)
        
        
        h_layout_buttons = QHBoxLayout()
        h_widget_buttons = QWidget()
        h_widget_buttons.setLayout(h_layout_buttons)
        
        apply_button = QPushButton()
        apply_button.setText("Apply")
        apply_button.clicked.connect(self.save_settings)
        h_layout_buttons.addWidget(apply_button)
        
        save_and_close = QPushButton()
        save_and_close.setText("Save && Close")
        save_and_close.clicked.connect(self.save_and_close)
        h_layout_buttons.addWidget(save_and_close)
        
        layout.addWidget(h_widget_buttons)
    
    def swudbapi_toggled(self):
        self.configuration_manager.set_image_source(Configuration.Settings.ImageSource.SWUDBAPI)
        
    def swudb_toggled(self):
        self.configuration_manager.set_image_source(Configuration.Settings.ImageSource.SWUDB)
    
    def state_changed(self, state):
        if state == 2:
            self.configuration_manager.toggle_performance_mode(True)
        else:
            self.configuration_manager.toggle_performance_mode(False)
            
    def save_and_close(self):
        self.save_settings()
        self.close()
    
    def save_settings(self):
        self.configuration_manager.save()