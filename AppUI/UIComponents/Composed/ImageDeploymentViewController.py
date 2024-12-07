from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QSizePolicy,
                             QVBoxLayout, QWidget)

from AppCore import ConfigurationProviderProtocol, ObservationTower
from AppCore.Models import LocalCardResource
from AppCore.Observation.Events import (ConfigurationUpdatedEvent, SearchEvent,
                                        TransmissionProtocol)
from AppUI.UIComponents.Base.ImagePreviewViewController import *


class ImageDeploymentViewControllerDelegate:
    def id_did_tap_staging_button(self, id: ...) -> None:
        pass
    
    def id_did_tap_unstaging_button(self, id: ...) -> None:
        pass

class ImageDeploymentViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 configuration_provider: ConfigurationProviderProtocol, 
                 image_preview_delegate: ImagePreviewViewControllerDelegate, 
                 asset_provider: AssetProvider):
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
        # https://www.qtcentre.org/threads/18363-QScrollArea-How-to-avoid-automatic-scroll-actions?p=232187#post232187
        unstage_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        unstage_button.setText("Unstage")
        unstage_button.clicked.connect(self.tapped_unstaging_button)
        unstage_button.setEnabled(False)
        self.unstage_button = unstage_button
        first_column_layout.addWidget(unstage_button)

        first_column_widget = QWidget()
        first_column_widget.setMaximumHeight(150)
        first_column_widget.setLayout(first_column_layout)
        # first_column_widget.setFixedWidth(200)
        layout.addWidget(first_column_widget)

        staging_image_view = ImagePreviewViewController(observation_tower, 
                                                        configuration_provider, 
                                                        asset_provider)
        staging_image_view.delegate = image_preview_delegate
        layout.addWidget(staging_image_view, 4)
        self.staging_image_view = staging_image_view

        production_image_view = ImagePreviewViewController(observation_tower, 
                                                           configuration_provider, 
                                                           asset_provider)
        production_image_view.delegate = image_preview_delegate
        layout.addWidget(production_image_view, 4)
        self.production_image_view = production_image_view

        self.setLayout(vertical_layout)

        self.delegate: Optional[ImageDeploymentViewControllerDelegate] = None
        
        observation_tower.subscribe(self, SearchEvent)
        observation_tower.subscribe(self, ConfigurationUpdatedEvent)
    
    
    def set_staging_image(self, local_resource: LocalCardResource):
        self.staging_image_view.set_image(local_resource)
        self.set_unstage_button_enabled(True)

    def clear_staging_image(self):
        self.staging_image_view.clear_image()
        self.set_unstage_button_enabled(False)

    def set_production_image(self, local_resource: LocalCardResource):
        self.production_image_view.set_image(local_resource)
        self._local_resource = local_resource
        self.label.setText(local_resource.display_name)
        

    def tapped_staging_button(self):
        if self.delegate is not None:
            self.delegate.id_did_tap_staging_button(self)
    
    def tapped_unstaging_button(self):
        if self.delegate is not None:
            self.delegate.id_did_tap_unstaging_button(self)

    def set_unstage_button_enabled(self, enabled: bool):
        self.unstage_button.setEnabled(enabled)
        if enabled:
            self.unstage_button.setStyleSheet("background-color : #d2232a; color: white;")
        else:
            self.unstage_button.setStyleSheet("")

    def set_staging_button_enabled(self, enabled: bool):
        self.stage_button.setEnabled(enabled)
        if enabled:
            self.stage_button.setStyleSheet("background-color : #fdb933; color: black;")
        else:
            self.stage_button.setStyleSheet("")
    
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == SearchEvent:
            if event.event_type == SearchEvent.EventType.STARTED:
                pass
            elif event.event_type == SearchEvent.EventType.FINISHED:
                pass
        elif type(event) == ConfigurationUpdatedEvent:
            pass
