from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QHBoxLayout, QPushButton, QScrollArea,
                             QSizePolicy, QVBoxLayout, QWidget)

from AppCore.Config import Configuration
from AppCore.DataSource.DataSourceSelectedLocalCardResource import *
from AppCore.ImageResource.ImageResourceProcessorProtocol import *
from AppCore.Observation import *
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        LocalCardResourceFetchEvent,
                                        LocalCardResourceSelectedEvent,
                                        ProductionCardResourcesLoadEvent,
                                        PublishStagedCardResourcesEvent,
                                        PublishStatusUpdatedEvent)
from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding

from .LoadingSpinner import LoadingSpinner
from ..Base import ImageDeploymentViewController


class ImageDeploymentListViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesInternalProviding,
                 local_resource_data_source_provider: LocalResourceDataSourceProviding):
        super().__init__()
        self._app_dependencies_provider = app_dependencies_provider
        self._observation_tower = app_dependencies_provider.observation_tower
        self._data_source_image_resource_deployer = app_dependencies_provider.data_source_image_resource_deployer
        self._local_resource_data_source_provider = local_resource_data_source_provider
        self._router = app_dependencies_provider.router
        self._external_app_dependencies_provider = app_dependencies_provider.external_app_dependencies_provider

        self._setup_view()

        self._observation_tower.subscribe_multi(self, [PublishStatusUpdatedEvent, 
                                                      LocalCardResourceFetchEvent, 
                                                      PublishStagedCardResourcesEvent, 
                                                      LocalCardResourceSelectedEvent, 
                                                      ProductionCardResourcesLoadEvent, 
                                                      ConfigurationUpdatedEvent])
        
        app_dependencies_provider.shortcut_action_coordinator.bind_publish(self.tapped_production_button, self)
        
    def _setup_view(self):
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
        
        
        image_deployer_banner_cta = self._external_app_dependencies_provider.provide_image_deployer_banner_cta(self._data_source_image_resource_deployer, self._router)
        if image_deployer_banner_cta is not None:
            self.add_image_cta = image_deployer_banner_cta
            cells_container_layout.addWidget(image_deployer_banner_cta)
        
        
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
            
    @property
    def _configuration(self) -> Configuration:
        return self._app_dependencies_provider.configuration_manager.configuration

    def clear_list(self):
        for i in reversed(range(self._deployment_cells_layout.count())):
            layout_item = self._deployment_cells_layout.takeAt(i)
            if layout_item is not None:
                widget = layout_item.widget()
                if widget is not None:
                    widget.deleteLater()
        self.list_items = []

    def _reload_production_resources_list(self):
        self.clear_list()
        
        is_deployment_list_horizontal = self._configuration.is_deployment_list_horizontal
        
        if is_deployment_list_horizontal:
            deployment_cells_layout = QHBoxLayout()
        else:
            deployment_cells_layout = QVBoxLayout()
        deployment_cells_layout.setContentsMargins(0, 0, 0, 0)
        deployment_cells_widget = QWidget()
        deployment_cells_widget.setLayout(deployment_cells_layout)
        self._deployment_cells_layout.addWidget(deployment_cells_widget)
        
        card_resources = self._data_source_image_resource_deployer.deployment_resources
        for index, deployment_resource in enumerate(card_resources):
            item = ImageDeploymentViewController(self._app_dependencies_provider, 
                                                 deployment_resource,
                                                 self._local_resource_data_source_provider, 
                                                 not is_deployment_list_horizontal)
            if index <= 9:
                item.stage_button.setText(f'Stage (Ctrl+{index + 1})')
                self._app_dependencies_provider.shortcut_action_coordinator.bind_stage(item.tapped_staging_button, index, item)
                item.unstage_button.setText(f'Unstage (Alt+{index + 1})')
                self._app_dependencies_provider.shortcut_action_coordinator.bind_unstage(item.tapped_unstaging_button, index, item)
            else:
                item.stage_button.setText(f'Stage')
                item.unstage_button.setText(f'Unstage')
            
            pal = item.palette()
            pal.setColor(item.backgroundRole(), Qt.GlobalColor.lightGray)
            item.setAutoFillBackground(True)
            item.setPalette(pal)
            deployment_cells_layout.addWidget(item)

            self.list_items.append(item)

    def tapped_production_button(self):
        self.publish_to_production()
            
    def publish_to_production(self):
        if self._data_source_image_resource_deployer.can_publish_staged_resources:
            try:
                self._data_source_image_resource_deployer.publish_staged_resources()
            except Exception as error:
                # failed to publish
                # show error messages
                self._router.show_error(error)
                self._reload_production_resources_list()

    def set_production_button_enabled(self, enabled: bool):
        self.production_button.setEnabled(enabled)
        if enabled:
            self.production_button.setStyleSheet("background-color : #41ad49; color: white;")
        else:
            self.production_button.setStyleSheet("")
    
    def _sync_configuration_related_components(self):
        self._reload_production_resources_list()


    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if (type(event) == PublishStatusUpdatedEvent or 
            type(event) == LocalCardResourceFetchEvent or 
            type(event) == PublishStagedCardResourcesEvent):
            can_publish_staged_resources = self._data_source_image_resource_deployer.can_publish_staged_resources
            self.set_production_button_enabled(can_publish_staged_resources)
        # if type(event) == PublishStagedCardResourcesEvent:
        #     if (event.event_type == PublishStagedCardResourcesEvent.EventType.FINISHED or 
        #         event.event_type == PublishStagedCardResourcesEvent.EventType.FAILED):
        #         self._reload_production_resources_list()
        if type(event) == ProductionCardResourcesLoadEvent:
            if event.event_type == ProductionCardResourcesLoadEvent.EventType.STARTED:
                self.loading_spinner.start()
            elif event.event_type == ProductionCardResourcesLoadEvent.EventType.FINISHED:
                self._reload_production_resources_list()
                self.loading_spinner.stop()
            
        if type(event) == ConfigurationUpdatedEvent:
            self._sync_configuration_related_components()
            
            if (event.configuration.deployment_list_sort_is_desc_order != event.old_configuration.deployment_list_sort_is_desc_order or 
                event.configuration.deployment_list_sort_criteria != event.old_configuration.deployment_list_sort_criteria):
                self._data_source_image_resource_deployer.load_production_resources()