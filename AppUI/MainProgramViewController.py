from typing import List, Optional

from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWidgets import (QHBoxLayout, QInputDialog, QMessageBox, QSplitter,
                             QWidget)

from AppCore.ApplicationCore import ApplicationCore
from AppCore.Config import ConfigurationProviderProtocol
from AppCore.Data import APIClientProviderProtocol
from AppCore.Models import LocalCardResource, SearchConfiguration, TradingCard
from AppCore.Observation import *
from AppCore.Resource import CardImageSourceProviderProtocol
from AppUI.UIComponents import (AddImageCTAViewController,
                                AddImageCTAViewControllerDelegate,
                                CardSearchPreviewViewController,
                                ImageDeploymentListViewController,
                                ImageDeploymentViewController, SearchTableView)
from AppUI.UIComponents.Base.ImagePreviewViewController import (
    ImagePreviewViewController, ImagePreviewViewControllerDelegate)

from .Assets import AssetProvider
from .PopoutImageManager import PopoutImageManager


class MainProgramViewController(QWidget, 
                                ImagePreviewViewControllerDelegate, 
                                AddImageCTAViewControllerDelegate):
    def __init__(self,
                 observation_tower: ObservationTower,
                 configuration_provider: ConfigurationProviderProtocol,
                 application_core: ApplicationCore, 
                 card_search_source_provider: APIClientProviderProtocol,
                 card_image_source_provider: CardImageSourceProviderProtocol, 
                 asset_provider: AssetProvider):
        super().__init__()
        
        self.sound_effect = None
        self._asset_provider = asset_provider
        self._observation_tower = observation_tower

        application_core.delegate = self
        self.application_core = application_core

        horizontal_layout = QHBoxLayout()
        self.setLayout(horizontal_layout)
        
        splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        horizontal_layout.addWidget(splitter)
        

        card_search_view = CardSearchPreviewViewController(observation_tower, 
                                                           configuration_provider,
                                                           card_search_source_provider,
                                                           card_image_source_provider, 
                                                           asset_provider)
        card_search_view.setObjectName('stuff')
        self.setStyleSheet('QWidget#stuff { background-color:red; }')
        card_search_view.delegate = self
        card_search_view.set_search_focus()
        self.card_search_view = card_search_view
        splitter.addWidget(card_search_view)

        self.popout_manager = PopoutImageManager(observation_tower, 
                                                 configuration_provider)

        deployment_view = ImageDeploymentListViewController(observation_tower, 
                                                            configuration_provider, 
                                                            asset_provider, 
                                                            self, 
                                                            self.application_core)
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
        staging_button_enabled = self.application_core.current_card_search_resource is not None
        self.deployment_view.load_production_resources(card_resources, staging_button_enabled)

    def app_did_complete_search(self, app: ApplicationCore, result_list: List[TradingCard], error: Optional[Exception]):
        self.card_search_view.update_list(result_list)

    def app_did_retrieve_card_resource_for_card_selection(self, app: ApplicationCore, card_resource: LocalCardResource, is_flippable: bool):
        self.card_search_view.set_image(is_flippable, card_resource)

    # search table view
    def tv_did_tap_search(self, table_view: SearchTableView, search_configuration: SearchConfiguration):
        self.application_core.search(search_configuration)
        

    def tv_did_select(self, table_view: SearchTableView, index: int):
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

    def confirm_unstage_all_resources(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Unstage all resources")
        dlg.setText("Are you sure you want to unstage all resources?")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) # type: ignore
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()

        if button == QMessageBox.StandardButton.Yes:
            self._unstage_all_resources()

    def _unstage_all_resources(self):
            self.deployment_view.clear_all_staging_images()
            self.application_core.unstage_all_resources()

    def confirm_clear_cache(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Clear cache")
        dlg.setText("Are you sure you want to clear the cache?")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) # type: ignore
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()

        if button == QMessageBox.StandardButton.Yes:
            self._unstage_all_resources()
            self.application_core.clear_cache()
        

    def shortcut_production_button(self):
        if self.application_core.can_publish_staged_resources:
            self.publish_staged_resources()
            
    def idl_did_tap_production_button(self, id_list: ImageDeploymentListViewController):
        self.publish_staged_resources()
    
    def _play_sound_effect(self):
        self.sound_effect = QSoundEffect()
        self.sound_effect.setVolume(0.5)
        self.sound_effect.setSource(QUrl.fromLocalFile(self._asset_provider.audio.r4_affirmative_path))
        print(f'playing sound effect: {self._asset_provider.audio.r4_effect_path}')
        self.sound_effect.play()

    def publish_staged_resources(self):
        try:
            self.application_core.publish_staged_resources()
            # self._play_sound_effect()
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

    def flip_current_previewed_card_if_possible(self):
        if self.application_core.current_previewed_trading_card_is_flippable():
            self.application_core.flip_current_previewed_card()
    
    # MARK: - ImagePreviewViewControllerDelegate
    def ip_rotate_resource(self, ip: ImagePreviewViewController, local_resource: LocalCardResource, angle: float):
        self.application_core.rotate_and_save_resource(local_resource, angle)
        
    def ip_regenerate_preview(self, ip: ImagePreviewViewController, local_resource: LocalCardResource):
        self.application_core.regenerate_resource_preview(local_resource)
        
    def ip_redownload_resource(self, ip: ImagePreviewViewController, local_resource: LocalCardResource):
        self.application_core.redownload_resource(local_resource)
    
    def ip_open_file(self, ip: ImagePreviewViewController, local_resource: LocalCardResource):
        self.application_core.open_file(local_resource)

    def ip_open_file_path_and_select_file(self, ip: ImagePreviewViewController, local_resource: LocalCardResource):
        self.application_core.open_file_path_and_select_file(local_resource)

    def prompt_generate_new_file(self):
        text, ok = QInputDialog.getText(self, 'Create new image file', 'Enter file name:')
        if ok:
            self.generate_new_file(text)
            self.load()
            
    def generate_new_file(self, file_name: str):
        try:
            self.application_core.generate_new_file(file_name, Image.open(self._asset_provider.image.swu_logo_black_path))
        except Exception as error:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Icon.Critical)
            msgBox.setText(str(error))
            msgBox.setWindowTitle("Error")
            msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
            msgBox.exec()
        
    
    def regenerate_production_file(self, local_resource: LocalCardResource):
        self.generate_new_file(local_resource.file_name)
        
    def aicta_did_tap_generate_button(self, aicta: AddImageCTAViewController):
        self.prompt_generate_new_file()

    # Platform operations
    def open_production_dir(self):
        self.application_core.open_production_dir()
        
    def open_configuration_dir(self):
        self.application_core.open_configuration_dir()

    def open_temp_dir(self):
        self.application_core.open_temp_dir()