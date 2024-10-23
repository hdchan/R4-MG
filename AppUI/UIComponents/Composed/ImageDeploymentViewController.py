from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QPushButton,
                             QVBoxLayout, QWidget, QSizePolicy)

from AppCore import ConfigurationProvider, ObservationTower
from AppCore.Models import LocalCardResource
from AppCore.Observation.Events import SearchEvent, TransmissionProtocol, ConfigurationUpdatedEvent
from AppUI.UIComponents import ImagePreviewViewController

class ImageDeploymentViewController(QWidget):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 configuration_provider: ConfigurationProvider):
        super().__init__()
        self.observation_tower = observation_tower
        self.configuration_provider = configuration_provider
        vertical_layout = QVBoxLayout()
        
        label = QLabel()
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        label.setWordWrap(True)
        font = label.font()
        font.setBold(True)
        font.setPointSize(12)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignLeading)
        vertical_layout.addWidget(label)
        self.label = label

        layout = QHBoxLayout()
        layout_widget = QWidget()
        layout_widget.setLayout(layout)
        
        vertical_layout.addWidget(label)
        vertical_layout.addWidget(layout_widget)
        
        first_column_layout = QVBoxLayout()

        stage_button = QPushButton()
        stage_button.setText("Stage")
        stage_button.clicked.connect(self.tapped_staging_button)
        stage_button.setEnabled(False)
        self.stage_button = stage_button
        first_column_layout.addWidget(stage_button)
        
        unstage_button = QPushButton()
        unstage_button.setText("Unstage")
        unstage_button.clicked.connect(self.tapped_unstaging_button)
        unstage_button.setEnabled(False)
        self.unstage_button = unstage_button
        first_column_layout.addWidget(unstage_button)

        first_column_widget = QWidget()
        first_column_widget.setMaximumHeight(150)
        first_column_widget.setLayout(first_column_layout)
        first_column_widget.setFixedWidth(150)
        layout.addWidget(first_column_widget)

        staging_image_view = ImagePreviewViewController(observation_tower, 
                                                        configuration_provider)
        layout.addWidget(staging_image_view, 4)
        self.staging_image_view = staging_image_view

        production_image_view = ImagePreviewViewController(observation_tower, 
                                                           configuration_provider)
        layout.addWidget(production_image_view, 4)
        self.production_image_view = production_image_view

        self.setLayout(vertical_layout)

        self.delegate = None
        
        observation_tower.subscribe(self, SearchEvent)
        observation_tower.subscribe(self, ConfigurationUpdatedEvent)
      
    def set_staging_image(self, local_resource: LocalCardResource):
        self.staging_image_view.set_image(local_resource.display_name, local_resource.image_preview_path)
        self.set_unstage_button_enabled(True)

    def clear_staging_image(self):
        self.staging_image_view.clear_image()
        self.set_unstage_button_enabled(False)

    def set_production_image(self, local_resource: LocalCardResource):
        self.production_image_view.set_image(local_resource.display_name, local_resource.image_preview_path)
        self._local_resource = local_resource
        self.label.setText(local_resource.display_name)
        

    def tapped_staging_button(self):
        self.delegate.id_did_tap_staging_button(self)
        

    def set_unstage_button_enabled(self, enabled: bool):
        self.unstage_button.setEnabled(enabled)
        if enabled:
            self.unstage_button.setStyleSheet("background-color : #FA9189")
        else:
            self.unstage_button.setStyleSheet("")

    def set_staging_button_enabled(self, enabled: bool):
        self.stage_button.setEnabled(enabled)
        if enabled:
            self.stage_button.setStyleSheet("background-color : #FFE699")
        else:
            self.stage_button.setStyleSheet("")

    def tapped_unstaging_button(self):
        self.delegate.id_did_tap_unstaging_button(self)

    
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == SearchEvent:
            if event.event_type == SearchEvent.EventType.STARTED:
                pass
            elif event.event_type == SearchEvent.EventType.FINISHED:
                pass
        elif type(event) == ConfigurationUpdatedEvent:
            pass
