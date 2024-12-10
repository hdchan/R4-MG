from typing import List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMessageBox, QPushButton, QScrollArea,
                             QSizePolicy, QVBoxLayout, QWidget)

from AppCore.Data.LocalResourceDataSourceProtocol import *
from AppCore.Image.ImageResourceDeployer import ImageResourceDeployer
from AppCore.Image.ImageResourceProcessorProtocol import *
from AppCore.Models import LocalCardResource
from AppCore.Observation import *
from AppCore.Observation.Events import (LocalResourceFetchEvent,
                                        LocalResourceSelectedEvent,
                                        ProductionResourcesLoadedEvent,
                                        PublishStagedResourcesEvent,
                                        PublishStatusUpdatedEvent)
from AppUI.AppDependencyProviding import AppDependencyProviding

from ..Base import AddImageCTAViewController
from ..Base.LoadingSpinner import LoadingSpinner
from . import ImageDeploymentViewController


class ImageDeploymentListViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 app_dependency_provider: AppDependencyProviding,
                 image_resource_deployer: ImageResourceDeployer,
                 local_resource_data_source_provider: LocalResourceDataSourceProviding):
        super().__init__()
        self.app_dependency_provider = app_dependency_provider
        self.observation_tower = app_dependency_provider.observation_tower
        self.configuration_manager = app_dependency_provider.configuration_manager
        self.asset_provider = app_dependency_provider.asset_provider
        self._image_resource_deployer = image_resource_deployer
        self._local_resource_data_source_provider = local_resource_data_source_provider
        self.image_resource_processor_provider = app_dependency_provider.image_resource_processor_provider

        outer_container_layout = QVBoxLayout()
        self.setLayout(outer_container_layout)
        
        cells_container_layout = QVBoxLayout()
        cells_container_layout.setContentsMargins(0, 0, 0, 0)
        cells_container_widget = QWidget()
        cells_container_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed) # prevent stretching of container in scroll view
        cells_container_widget.setLayout(cells_container_layout)
        
        deployment_cells_layout = QVBoxLayout()
        deployment_cells_layout.setContentsMargins(0, 0, 0, 0)
        deployment_cells_widget = QWidget()
        deployment_cells_widget.setLayout(deployment_cells_layout)
        self._deployment_cells_layout = deployment_cells_layout
        cells_container_layout.addWidget(deployment_cells_widget)
        
        
        add_image_cta = AddImageCTAViewController(app_dependency_provider.asset_provider)
        self.add_image_cta = add_image_cta
        cells_container_layout.addWidget(add_image_cta)
        
        
        self.scroll_view = QScrollArea(self)
        self.scroll_view.setWidget(cells_container_widget)
        self.scroll_view.setWidgetResizable(True)
        outer_container_layout.addWidget(self.scroll_view)
        

        production_button = QPushButton()
        production_button.setText("Production (Ctrl+P)")
        production_button.setEnabled(False)
        production_button.clicked.connect(self.tapped_production_button)
        self.production_button = production_button
        outer_container_layout.addWidget(production_button)

        self.list_items: List[ImageDeploymentViewController] = []
        
        self.loading_spinner = LoadingSpinner(self)
        
        self.observation_tower.subscribe_multi(self, [PublishStatusUpdatedEvent, 
                                                      LocalResourceFetchEvent, 
                                                      PublishStagedResourcesEvent, 
                                                      LocalResourceSelectedEvent, 
                                                      ProductionResourcesLoadedEvent])
    
    @property
    def local_resource_data_source(self) -> LocalResourceDataSourceProtocol:
        return self._local_resource_data_source_provider.data_source

    def load_production_resources(self, card_resources: List[LocalCardResource], staging_button_enabled: bool):
        for index, resource in enumerate(card_resources):
            self._create_list_item(resource,
                                   staging_button_enabled,
                                   index)
            
    def _create_list_item(self,
                         local_resource: LocalCardResource,
                         staging_button_enabled: bool,
                         index: int):
        item = ImageDeploymentViewController(self.app_dependency_provider,
                                             self.image_preview_delegate)
        item.delegate = self
        item.set_production_image(local_resource)
        if index <= 9:
            item.stage_button.setText(f'Stage (Ctrl+{index + 1})')
        else:
            item.stage_button.setText(f'Stage')
        item.set_staging_button_enabled(staging_button_enabled)
        
        pal = item.palette()
        pal.setColor(item.backgroundRole(), Qt.GlobalColor.lightGray)
        item.setAutoFillBackground(True)
        item.setPalette(pal)
        self._deployment_cells_layout.addWidget(item)

        self.list_items.append(item)

    def clear_list(self):
        for i in reversed(range(self._deployment_cells_layout.count())):
            layout_item = self._deployment_cells_layout.takeAt(i)
            if layout_item is not None:
                widget = layout_item.widget()
                if widget is not None:
                    widget.deleteLater()
        self.list_items = []

    def id_did_tap_staging_button(self, id_cell: ImageDeploymentViewController):
        for idx, i in enumerate(self.list_items):
            if i == id_cell:
                self.stage_current_image(idx)

    def stage_current_image(self, idx: int):
        local_resource = self.local_resource_data_source.selected_local_resource
        if local_resource is not None:
            self._image_resource_deployer.stage_resource(local_resource, idx)
            self.set_staging_image(local_resource, idx)

    def id_did_tap_unstaging_button(self, id_cell: ImageDeploymentViewController):
        for idx, i in enumerate(self.list_items):
            if i == id_cell:
                self._image_resource_deployer.unstage_resource(idx)
                self.clear_staging_image(idx)

    def set_staging_image(self, local_resource: LocalCardResource, index: int):
        self.list_items[index].set_staging_image(local_resource)

    def clear_staging_image(self, index: int):
        self.list_items[index].clear_staging_image()
    
    def set_production_image(self, local_resource: LocalCardResource, index: int):
        self.list_items[index].set_production_image(local_resource)


    def clear_all_staging_images(self):
        for i in self.list_items:
            i.clear_staging_image()

    def tapped_production_button(self):
        self.publish_to_production()
            
    def publish_to_production(self):
        if self.local_resource_data_source.selected_local_resource is not None:
            try:
                self._image_resource_deployer.publish_staged_resources()
                self._image_resource_deployer.load_production_resources()
            except Exception as error:
                # failed to publish
                # show error messages
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Icon.Critical)
                msgBox.setText(str(error))
                msgBox.setWindowTitle("Error")
                msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
                msgBox.exec()
        
    def set_all_staging_button_enabled(self, enabled: bool):
        for i in self.list_items:
            i.set_staging_button_enabled(enabled)

    def set_production_button_enabled(self, enabled: bool):
        self.production_button.setEnabled(enabled)
        if enabled:
            self.production_button.setStyleSheet("background-color : #41ad49; color: white;")
        else:
            self.production_button.setStyleSheet("")

    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if (type(event) == PublishStatusUpdatedEvent or 
            type(event) == LocalResourceFetchEvent):
            can_publish_staged_resources = self._image_resource_deployer.can_publish_staged_resources
            self.set_production_button_enabled(can_publish_staged_resources)

        if type(event) == LocalResourceSelectedEvent:
            self.set_all_staging_button_enabled(True)

        if type(event) == ProductionResourcesLoadedEvent:
            production_resources = self._image_resource_deployer.production_resources
            staging_button_enabled = self.local_resource_data_source.selected_local_resource is not None
            self.clear_list()
            self.load_production_resources(production_resources, staging_button_enabled)