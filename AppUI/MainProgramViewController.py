from typing import List, Optional

from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWidgets import (QHBoxLayout, QInputDialog, QMessageBox, QSplitter,
                             QWidget)

from AppCore.Data.CardSearchDataSource import (CardSearchDataSource,
                                               CardSearchDataSourceDelegate)
from AppCore.Image.ImageResourceDeployer import ImageResourceDeployer
from AppCore.Models import LocalCardResource, TradingCard
from AppCore.Observation import *
from AppUI.AppDependencyProviding import AppDependencyProviding
from AppUI.UIComponents import (AddImageCTAViewController,
                                AddImageCTAViewControllerDelegate,
                                CardSearchPreviewViewController,
                                ImageDeploymentListViewController)
from AppUI.UIComponents.Base.ImagePreviewViewController import (
    ImagePreviewViewController, ImagePreviewViewControllerDelegate)


class MainProgramViewController(QWidget, 
                                ImagePreviewViewControllerDelegate, 
                                AddImageCTAViewControllerDelegate, 
                                CardSearchDataSourceDelegate):
    def __init__(self,
                 app_dependency_provider: AppDependencyProviding,
                 card_search_data_source: CardSearchDataSource,
                 image_resource_deployer: ImageResourceDeployer,
                 card_search_preview_view_controller: CardSearchPreviewViewController,
                 deployment_view_controller: ImageDeploymentListViewController):
        super().__init__()
        
        self.sound_effect = None
        self._asset_provider = app_dependency_provider.asset_provider
        self._observation_tower = app_dependency_provider.observation_tower
        self._platform_service_provider = app_dependency_provider.platform_service_provider
        self._image_resource_deployer = image_resource_deployer


        self._card_search_data_source = card_search_data_source
        self._card_search_data_source.delegate = self

        horizontal_layout = QHBoxLayout()
        self.setLayout(horizontal_layout)
        
        splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        horizontal_layout.addWidget(splitter)
        
        self.card_search_view = card_search_preview_view_controller
        self.card_search_view.set_search_focus()
        
        splitter.addWidget(self.card_search_view)

        
        self.deployment_view = deployment_view_controller
        splitter.addWidget(deployment_view_controller)
        splitter.setSizes([400,900])


    def set_search_bar_focus(self):
        self.card_search_view.set_search_focus()

    def search(self):
        self.card_search_view.search()
        
    def search_leader(self):
        self.card_search_view.search_leader()
        
    def search_base(self):
        self.card_search_view.search_base()

    def ds_completed_search_with_result(self, ds: CardSearchDataSource, result_list: List[TradingCard], error: Optional[Exception]):
        self.card_search_view.update_list(result_list)

    def ds_did_retrieve_card_resource_for_card_selection(self, ds: CardSearchDataSource, local_resource: LocalCardResource, is_flippable: bool):
        self.card_search_view.set_image(is_flippable, local_resource)


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
            self._image_resource_deployer.unstage_all_resources()

    def confirm_clear_cache(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Clear cache")
        dlg.setText("Are you sure you want to clear the cache?")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) # type: ignore
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()

        if button == QMessageBox.StandardButton.Yes:
            self._unstage_all_resources()
            self._platform_service_provider.platform_service.clear_cache()
        

    # TODO: fix
    # def shortcut_production_button(self):
    #     if self.application_core.can_publish_staged_resources:
    #         self.publish_staged_resources()
    
    def _play_sound_effect(self):
        self.sound_effect = QSoundEffect()
        self.sound_effect.setVolume(0.5)
        self.sound_effect.setSource(QUrl.fromLocalFile(self._asset_provider.audio.r4_affirmative_path))
        print(f'playing sound effect: {self._asset_provider.audio.r4_effect_path}')
        self.sound_effect.play()

    
    # MARK: - ImagePreviewViewControllerDelegate
    def prompt_generate_new_file(self):
        text, ok = QInputDialog.getText(self, 'Create new image file', 'Enter file name:')
        if ok:
            self.generate_new_file(text)
            self._image_resource_deployer.load_production_resources()
    
    def ip_regenerate_production_file(self, ip: ImagePreviewViewController, local_resource: LocalCardResource):
        self.generate_new_file(local_resource.file_name)

    # TODO consolidate this
    def generate_new_file(self, file_name: str):
        try:
            self._image_resource_deployer.generate_new_file(file_name, Image.open(self._asset_provider.image.swu_logo_black_path))
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
