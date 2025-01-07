from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QPushButton, QScrollArea, QSizePolicy,
                             QVBoxLayout, QWidget, QLabel)

from AppCore.Data.LocalResourceDataSourceProtocol import *
from AppCore.Image.ImageResourceProcessorProtocol import *
from AppCore.Config import Configuration
from AppCore.Observation import *
from AppCore.Observation.Events import (LocalResourceFetchEvent,
                                        LocalResourceSelectedEvent,
                                        ProductionResourcesLoadEvent,
                                        PublishStagedResourcesEvent,
                                        PublishStatusUpdatedEvent, 
                                        ConfigurationUpdatedEvent)
from AppUI.AppDependencyProviding import AppDependencyProviding

from ..Base import AddImageCTAViewController
from ..Base.LoadingSpinner import LoadingSpinner
from . import ImageDeploymentViewController


class ImageDeploymentListViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 app_dependency_provider: AppDependencyProviding,
                 local_resource_data_source_provider: LocalResourceDataSourceProviding):
        super().__init__()
        self.app_dependency_provider = app_dependency_provider
        self._observation_tower = app_dependency_provider.observation_tower
        self._image_resource_deployer = app_dependency_provider.image_resource_deployer
        self._local_resource_data_source_provider = local_resource_data_source_provider
        self._router = app_dependency_provider.router

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
        
        
        add_image_cta = AddImageCTAViewController(app_dependency_provider)
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
        
        self.resize_prod_image_label = QLabel()
        self.resize_prod_image_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        outer_container_layout.addWidget(self.resize_prod_image_label)
        self._sync_resize_label_text()

        self.list_items: List[ImageDeploymentViewController] = []
        
        self.loading_spinner = LoadingSpinner(self)
        
        self._observation_tower.subscribe_multi(self, [PublishStatusUpdatedEvent, 
                                                      LocalResourceFetchEvent, 
                                                      PublishStagedResourcesEvent, 
                                                      LocalResourceSelectedEvent, 
                                                      ProductionResourcesLoadEvent, 
                                                      ConfigurationUpdatedEvent])
        
        app_dependency_provider.shortcut_action_coordinator.bind_publish(self.tapped_production_button, self)
        app_dependency_provider.menu_action_coordinator.bind_refresh_production_images(self._image_resource_deployer.load_production_resources)
    
    @property
    def _configuration(self) -> Configuration:
        return self.app_dependency_provider.configuration_manager.configuration
    
    @property
    def _local_resource_data_source(self) -> LocalResourceDataSourceProtocol:
        return self._local_resource_data_source_provider.data_source

    def load_production_resources(self):
        # TODO: custom ordering
        card_resources = self._image_resource_deployer.deployment_resources
        for index, deployment_resource in enumerate(card_resources):
            item = ImageDeploymentViewController(self.app_dependency_provider, 
                                                 deployment_resource,
                                                 self._local_resource_data_source_provider)
            if index <= 9:
                item.stage_button.setText(f'Stage (Ctrl+{index + 1})')
                self.app_dependency_provider.shortcut_action_coordinator.bind_stage(item.tapped_staging_button, index, item)
                item.unstage_button.setText(f'Unstage (Alt+{index + 1})')
                self.app_dependency_provider.shortcut_action_coordinator.bind_unstage(item.tapped_unstaging_button, index, item)
            else:
                item.stage_button.setText(f'Stage')
                item.unstage_button.setText(f'Unstage')
            
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
            

    def tapped_production_button(self):
        self.publish_to_production()
            
    def publish_to_production(self):
        if self._image_resource_deployer.can_publish_staged_resources:
            try:
                self._image_resource_deployer.publish_staged_resources()
                # self._image_resource_deployer.load_production_resources()
            except Exception as error:
                # failed to publish
                # show error messages
                self._router.show_error(error)

    def set_production_button_enabled(self, enabled: bool):
        self.production_button.setEnabled(enabled)
        if enabled:
            self.production_button.setStyleSheet("background-color : #41ad49; color: white;")
        else:
            self.production_button.setStyleSheet("")
        
    def _sync_resize_label_text(self):
        self.resize_prod_image_label.setHidden(not self._configuration.resize_prod_images)
        value = "-"
        if self._configuration.resize_prod_images:
            size = self._configuration.resize_prod_images_max_size
            value = f"Enabled to {size}px (min 256px)"
        else:
            value = "Disabled"
        self.resize_prod_image_label.setText(f"Resize prod images: {value}")
    
    def _sync_configuration_related_components(self):
        self._sync_resize_label_text()


    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if (type(event) == PublishStatusUpdatedEvent or 
            type(event) == LocalResourceFetchEvent or 
            type(event) == PublishStagedResourcesEvent):
            can_publish_staged_resources = self._image_resource_deployer.can_publish_staged_resources
            self.set_production_button_enabled(can_publish_staged_resources)

        if type(event) == ProductionResourcesLoadEvent:
            if event.event_type == ProductionResourcesLoadEvent.EventType.STARTED:
                self.loading_spinner.start()
            elif event.event_type == ProductionResourcesLoadEvent.EventType.FINISHED:
                self.clear_list()
                self.load_production_resources()
                self.loading_spinner.stop()
            
        if type(event) == ConfigurationUpdatedEvent:
            self._sync_configuration_related_components()
            
            if (event.configuration.deployment_list_sort_is_desc_order != event.old_configuration.deployment_list_sort_is_desc_order or 
                event.configuration.deployment_list_sort_criteria != event.old_configuration.deployment_list_sort_criteria):
                self._image_resource_deployer.load_production_resources()
            
            