from PyQt5 import QtCore
from PyQt5.QtWidgets import QHBoxLayout, QSplitter, QWidget

from AppCore import ApplicationCore
from AppCore.Config import Configuration
from AppCore.Models import LocalCardResource, CardType, SearchConfiguration
from AppCore.Observation import ObservationTower
from AppUI.UIComponents import (CardSearchPreviewViewController,
                                ImageDeploymentListViewController, ProfileLoaderViewController)

from typing import List, Optional
class MainProgramViewController(QWidget):
    def __init__(self,
                 observation_tower: ObservationTower,
                 configuration: Configuration,
                 application_core: ApplicationCore):
        super().__init__()

        application_core.delegate = self
        self.application_core = application_core

        horizontal_layout = QHBoxLayout()
        self.setLayout(horizontal_layout)
        
        splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        horizontal_layout.addWidget(splitter)
        

        card_search_view = CardSearchPreviewViewController(observation_tower, 
                                                           configuration, 
                                                           self.application_core.card_metadata_flow.card_type_list)
        card_search_view.delegate = self
        card_search_view.set_search_focus()
        self.card_search_view = card_search_view
        splitter.addWidget(card_search_view)

        deployment_view = ImageDeploymentListViewController(observation_tower, 
                                                            configuration)
        deployment_view.delegate = self
        self.deployment_view = deployment_view
        splitter.addWidget(deployment_view)
        
        # profile_loader_view = ProfileLoaderViewController()
        # splitter.addWidget(profile_loader_view)
        
        splitter.setSizes([150,400])

    def set_search_bar_focus(self):
        self.card_search_view.set_search_focus()

    def stage_current_card_search_resource(self, index: int):
        if self.application_core.can_stage_current_card_search_resource_to_stage_index(index) and self.application_core.card_search_flow.current_card_search_resource is not None:
            self.deployment_view.set_staging_image(self.application_core.card_search_flow.current_card_search_resource.display_name, self.application_core.card_search_flow.current_card_search_resource.image_preview_path, index)
            self.application_core.stage_resource(index)

    def load(self):
        self.application_core.load_production_resources()

    # app core
    def app_did_load_production_resources(self, app: ApplicationCore, card_resources: List[LocalCardResource]):
        self.deployment_view.clear_list()
        for index, r in enumerate(card_resources):
            file_name = r.file_name
            staging_button_enabled = self.application_core.card_search_flow.current_card_search_resource is not None
            self.deployment_view.create_list_item(f'File: {file_name}', 
                                                  file_name, 
                                                  r.image_preview_path, 
                                                  staging_button_enabled, 
                                                  index,
                                                  self.application_core.card_metadata_flow.card_type_list)

    def app_did_complete_search(self, app: ApplicationCore, result_list: List[str], error: Optional[Exception]):
        self.card_search_view.update_list(result_list)
        if len(result_list) > 0:
            self.card_search_view.set_item_active(0)

    def app_did_retrieve_card_resource_for_card_selection(self, app: ApplicationCore, card_resource: LocalCardResource, is_flippable: bool):
        self.card_search_view.set_image(card_resource.display_name, card_resource.image_preview_path, is_flippable)

    def app_publish_status_changed(self, app: ApplicationCore, is_ready: bool):
        self._update_production_button_state()
        
    def app_did_update_search_configuration(self, app: ApplicationCore, search_configuration: SearchConfiguration):
        self.card_search_view.set_card_type_filter(search_configuration.card_type)

    # search table view
    def tv_did_tap_search(self, table_view, card_name: str):
        self.application_core.card_search_flow.search(card_name)
        

    def tv_did_select(self, table_view, index: int):
        self.application_core.card_search_flow.select_card_resource_for_card_selection(index)
        self.deployment_view.set_all_staging_button_enabled(True)

    # card search
    def cs_did_tap_flip_button(self, cs):
        self.flip_current_previewed_card_if_possible()
        
    def tv_did_update_search_configuration(self, table_view, card_type: CardType):
        self.application_core.card_metadata_flow.set_search_configuration(card_type)


    # image deployment view
    def idl_did_tap_staging_button(self, id_list, id_cell, index: int):
        self.stage_current_card_search_resource(index)

    def idl_did_tap_unstaging_button(self, id_list, id_cell, index: int):
        self.deployment_view.clear_staging_image(index)
        self.application_core.unstage_resource(index)
        self._update_production_button_state()

    def idl_did_tap_unstage_all_button(self):
        self.deployment_view.clear_all_staging_images()
        self.application_core.unstage_all_resources()

    def idl_did_tap_production_button(self):
        self.publish_staged_resources()
        
    def idl_did_change_card_type(self, id_list, id_cell, index: int, card_type: CardType):
        self.application_core.card_metadata_flow.set_card_type_for_deployment_row(index, card_type)
            
    def publish_staged_resources(self):
        if self.application_core.can_publish_staged_resources():
            publish_success = self.application_core.publish_staged_resources()
            if  publish_success:
                self.application_core.load_production_resources()
                self._update_production_button_state()
                return

    def _update_production_button_state(self):
        production_button_enabled = self.application_core.can_publish_staged_resources()
        self.deployment_view.set_production_button_enabled(production_button_enabled)

    def flip_current_previewed_card_if_possible(self):
        if self.application_core.card_search_flow.current_previewed_trading_card_is_flippable():
            self.application_core.card_search_flow.flip_current_previewed_card()