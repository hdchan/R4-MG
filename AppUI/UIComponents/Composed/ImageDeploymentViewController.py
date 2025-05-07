from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QSizePolicy,
                             QVBoxLayout, QWidget)

from AppCore.Data.LocalResourceDataSourceProtocol import *
from AppCore.Image.ImageResourceProcessorProtocol import *
from AppCore.Models import DeploymentCardResource, LocalCardResource
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        DeploymentResourceEvent,
                                        TransmissionProtocol)
from AppUI.AppDependencyProviding import AppDependencyProviding
from AppUI.UIComponents.Base.ImagePreviewViewController import *


class ImageDeploymentViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 app_dependency_provider: AppDependencyProviding,
                 deployment_resource: DeploymentCardResource, 
                 local_resource_data_source_provider: LocalResourceDataSourceProviding, 
                 is_horizontal: bool):
        super().__init__()
        self._deployment_resource = deployment_resource
        self._local_resource_data_source_provider = local_resource_data_source_provider
        self._image_resource_deployer = app_dependency_provider.image_resource_deployer
        self._configuration_manager = app_dependency_provider.configuration_manager
        
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

        if is_horizontal:
            layout = QHBoxLayout()
        else:
            layout = QVBoxLayout()
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

        self._first_column_widget = QWidget()
        self._first_column_widget.setMaximumHeight(150)
        self._first_column_widget.setLayout(first_column_layout)
        # first_column_widget.setFixedWidth(200)
        layout.addWidget(self._first_column_widget)
        self._sync_configuration_state()

        staging_image_view = ImagePreviewViewController(app_dependency_provider)
        layout.addWidget(staging_image_view, 4)
        self.staging_image_view = staging_image_view

        production_image_view = ImagePreviewViewController(app_dependency_provider, False)
        layout.addWidget(production_image_view, 4)
        self.production_image_view = production_image_view

        self.setLayout(vertical_layout)

        
        app_dependency_provider.observation_tower.subscribe_multi(self, [DeploymentResourceEvent, 
                                                                         PublishStagedResourcesEvent, 
                                                                         PublishStatusUpdatedEvent, 
                                                                         LocalResourceSelectedEvent, 
                                                                         ConfigurationUpdatedEvent])
    
        self._sync_state()
    
    @property
    def _local_resource_data_source(self) -> LocalResourceDataSourceProtocol:
        return self._local_resource_data_source_provider.data_source
    
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
        

    def _sync_state(self):
        latest_deployment_resource = self._image_resource_deployer.latest_deployment_resource(self._deployment_resource)
        selected_resource = self._local_resource_data_source.selected_local_resource
        self.set_staging_button_enabled(selected_resource is not None)
        
        if latest_deployment_resource is not None:
            self.set_unstage_button_enabled(latest_deployment_resource.staged_resource is not None)
            if latest_deployment_resource.staged_resource is not None:
                self.set_staging_image(latest_deployment_resource.staged_resource)
            else:
                self.clear_staging_image()
            self.set_production_image(latest_deployment_resource.production_resource)

    def _sync_configuration_state(self):
        self._first_column_widget.setHidden(self._configuration_manager.configuration.hide_deployment_cell_controls)

    def tapped_staging_button(self):
        selected_resource = self._local_resource_data_source.selected_local_resource
        if selected_resource is not None:
            self._image_resource_deployer.stage_resource(self._deployment_resource, selected_resource)
    
    def tapped_unstaging_button(self):
        self._image_resource_deployer.unstage_resource(self._deployment_resource)

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
        if (type(event) == DeploymentResourceEvent or 
            type(event) == PublishStagedResourcesEvent or 
            type(event) == PublishStatusUpdatedEvent or 
            type(event) == LocalResourceSelectedEvent):
            self._sync_state()
        if type(event) == ConfigurationUpdatedEvent:
            self._sync_configuration_state()
        
