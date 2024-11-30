from typing import List, Optional

from PyQt5 import QtCore
from PyQt5.QtWidgets import QHBoxLayout, QSplitter, QWidget, QMessageBox

from AppCore import ApplicationCore
from AppCore.Config import ConfigurationProvider
from AppCore.Models import LocalCardResource, SearchConfiguration, TradingCard
from AppCore.Observation import ObservationTower
from AppCore.Resource import CardImageSourceProviderProtocol
from AppUI.UIComponents import (CardSearchPreviewViewController,
                                ImageDeploymentListViewController, ImageDeploymentViewController)
from AppUI.UIComponents.Base.ImagePreviewViewController import \
    ImagePreviewViewControllerDelegate
from Plugins import CardMetadataFlow

from .PopoutImageManager import PopoutImageManager

from .Assets import AssetProvider
class MainProgramViewController(QWidget, ImagePreviewViewControllerDelegate):
    def __init__(self,
                 observation_tower: ObservationTower,
                 configuration_provider: ConfigurationProvider,
                 application_core: ApplicationCore, 
                 card_image_source_provider: CardImageSourceProviderProtocol, 
                 asset_provider: AssetProvider):
        super().__init__()
        self._asset_provider = asset_provider
        
        self._card_metadata_flow = CardMetadataFlow(configuration_provider,
                                                    application_core)

        application_core.delegate = self
        self.application_core = application_core

        horizontal_layout = QHBoxLayout()
        self.setLayout(horizontal_layout)
        
        splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        horizontal_layout.addWidget(splitter)
        

        card_search_view = CardSearchPreviewViewController(observation_tower, 
                                                           configuration_provider, 
                                                           self._card_metadata_flow.card_type_list, 
                                                           card_image_source_provider, 
                                                           asset_provider)
        card_search_view.delegate = self
        card_search_view.set_search_focus()
        self.card_search_view = card_search_view
        splitter.addWidget(card_search_view)

        self.popout_manager = PopoutImageManager(observation_tower, 
                                                 configuration_provider)

        deployment_view = ImageDeploymentListViewController(observation_tower, 
                                                            configuration_provider)
        deployment_view.delegate = self
        self.deployment_view = deployment_view
        splitter.addWidget(deployment_view)
        
        # profile_loader_view = ProfileLoaderViewController()
        # splitter.addWidget(profile_loader_view)
        
        splitter.setSizes([400,900])

    def set_search_bar_focus(self):
        self.card_search_view.set_search_focus()

    def stage_current_card_search_resource(self, index: int):
        if self.application_core.can_stage_current_card_search_resource_to_stage_index(index) and self.application_core.current_card_search_resource is not None:
            self.deployment_view.set_staging_image(self.application_core.current_card_search_resource, index)
            self.application_core.stage_resource(index)

    def load(self):
        self.application_core.load_production_resources()

    def search(self):
        self.card_search_view.search()
        
    def search_leader(self):
        self.card_search_view.search_leader()
        
    def search_base(self):
        self.card_search_view.search_base()

    # app core
    def app_did_load_production_resources(self, app: ApplicationCore, card_resources: List[LocalCardResource]):
        self.deployment_view.clear_list()
        for index, r in enumerate(card_resources):
            file_name = r.file_name
            staging_button_enabled = self.application_core.current_card_search_resource is not None

            self.deployment_view.create_list_item(f'File: {file_name}', 
                                                  r, 
                                                  staging_button_enabled, 
                                                  index, 
                                                  self, 
                                                  self._asset_provider)

    def app_did_complete_search(self, app: ApplicationCore, result_list: List[TradingCard], error: Optional[Exception]):
        self.card_search_view.update_list(result_list)

    def app_did_retrieve_card_resource_for_card_selection(self, app: ApplicationCore, card_resource: LocalCardResource, is_flippable: bool):
        self.card_search_view.set_image(is_flippable, card_resource)

    def app_publish_status_changed(self, app: ApplicationCore, is_ready: bool):
        self._update_production_button_state()

    # search table view
    def tv_did_tap_search(self, table_view, search_configuration: SearchConfiguration):
        self.application_core.search(search_configuration)
        

    def tv_did_select(self, table_view, index: int):
        self.application_core.select_card_resource_for_card_selection(index)
        self.deployment_view.set_all_staging_button_enabled(True)

    # card search
    def cs_did_tap_flip_button(self, cs: CardSearchPreviewViewController):
        self.flip_current_previewed_card_if_possible()
        
    def cs_did_tap_retry_button(self, cs: CardSearchPreviewViewController):
        self.application_core.redownload_currently_selected_card_resource()


    # image deployment view
    def idl_did_tap_staging_button(self, 
                                   id_list: ImageDeploymentListViewController, 
                                   id_cell: ImageDeploymentViewController, 
                                   index: int):
        self.stage_current_card_search_resource(index)

    def idl_did_tap_unstaging_button(self, 
                                     id_list: ImageDeploymentListViewController, 
                                     id_cell: ImageDeploymentViewController,
                                     index: int):
        self.deployment_view.clear_staging_image(index)
        self.application_core.unstage_resource(index)
        self._update_production_button_state()
        
    def idl_did_tap_context_search_button(self, 
                                          id_list: ImageDeploymentListViewController, 
                                          id_cell: ImageDeploymentViewController, 
                                          index: int):
        self._card_metadata_flow.search_with_context_for_row(index)

    def idl_did_tap_unstage_all_button(self):
        self.deployment_view.clear_all_staging_images()
        self.application_core.unstage_all_resources()

    def idl_did_tap_production_button(self):
        if self.application_core.can_publish_staged_resources():
            self.publish_staged_resources()
            
    def publish_staged_resources(self):
        try:
            self.application_core.publish_staged_resources()
            self.application_core.load_production_resources()
        except Exception as error:
            # failed to publish
            # show error messages
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Icon.Critical)
            msgBox.setText(str(error))
            msgBox.setWindowTitle("Error")
            msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
            msgBox.exec()
        self._update_production_button_state()
        

    def _update_production_button_state(self):
        production_button_enabled = self.application_core.can_publish_staged_resources()
        self.deployment_view.set_production_button_enabled(production_button_enabled)

    def flip_current_previewed_card_if_possible(self):
        if self.application_core.current_previewed_trading_card_is_flippable():
            self.application_core.flip_current_previewed_card()
    
    # MARK: - ImagePreviewViewControllerDelegate
    def rotate_resource(self, local_resource: LocalCardResource, angle: float):
        self.application_core.rotate_and_save_resource(local_resource, angle)
        
    def regenerate_preview(self, local_resource: LocalCardResource):
        self.application_core.regenerate_resource_preview(local_resource)
        
    def redownload_resource(self, local_resource: LocalCardResource):
        self.application_core.redownload_resource(local_resource)