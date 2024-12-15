
from typing import Optional

from PIL import Image
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QWidget

from AppCore.Image.ImageResourceDeployer import ImageResourceDeployer
from AppCore.Service.PlatformServiceProvider import PlatformServiceProvider

from .Assets import AssetProvider
from .ComponentProvider import ComponentProviding
from .Coordinators.MenuActionCoordinator import MenuActionCoordinator


class Router:
    def __init__(self, 
                 image_resource_deployer: ImageResourceDeployer, 
                 asset_provider: AssetProvider, 
                 menu_action_coordinator: MenuActionCoordinator, 
                 component_provider: ComponentProviding, 
                 platform_service_provider: PlatformServiceProvider):
        self._image_resource_deployer = image_resource_deployer
        self._asset_provider = asset_provider
        self._component_provider = component_provider
        self._platform_service_provider = platform_service_provider

        menu_action_coordinator.bind_new_file(self.prompt_generate_new_file)
        menu_action_coordinator.bind_open_settings_page(self.open_settings_page)
        menu_action_coordinator.bind_open_about_page(self.open_about_page)
        menu_action_coordinator.bind_unstage_all_staging_resources(self.confirm_unstage_all_resources)
        menu_action_coordinator.bind_clear_cache_dir(self.confirm_clear_cache)
        
        self._settings_page: Optional[QWidget] = None
        self._about_page: Optional[QWidget] = None

    def prompt_generate_new_file(self):
        file_name, ok = QInputDialog.getText(None, 'Create new image file', 'Enter file name:')
        if ok:
            try:
                self._image_resource_deployer.generate_new_file(file_name, Image.open(self._asset_provider.image.swu_card_back))
                self._image_resource_deployer.load_production_resources()
            except Exception as error:
                self.show_error(error)

    def confirm_unstage_all_resources(self):
        dlg = QMessageBox()
        dlg.setWindowTitle("Unstage all resources")
        dlg.setText("Are you sure you want to unstage all resources?")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) # type: ignore
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()

        if button == QMessageBox.StandardButton.Yes:
            self._image_resource_deployer.unstage_all_resources()
            # needs to refresh UI

    def confirm_clear_cache(self):
        dlg = QMessageBox()
        dlg.setWindowTitle("Clear cache")
        dlg.setText("Are you sure you want to clear the cache?")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) # type: ignore
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()

        if button == QMessageBox.StandardButton.Yes:
            self._platform_service_provider.platform_service.clear_cache()

    def open_settings_page(self):
        def remove_ref():
            self._settings_page = None
        if self._settings_page is None or self._settings_page.isHidden():
            self._settings_page = self._component_provider.settings_view
            self._settings_page.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            self._settings_page.destroyed.connect(remove_ref)
            self._settings_page.show()
        if not self._settings_page.isHidden():
            self._settings_page.activateWindow()

    def open_about_page(self):
        def remove_ref():
            self._about_page = None
        if self._about_page is None or self._about_page.isHidden():
            self._about_page = self._component_provider.about_view
            self._about_page.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            # https://stackoverflow.com/a/65357051
            self._about_page.destroyed.connect(remove_ref)
            self._about_page.show()
        if not self._about_page.isHidden():
            self._about_page.activateWindow()
    
    def show_error(self, error: Exception):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Icon.Critical)
        msgBox.setText(str(error))
        msgBox.setWindowTitle("Error")
        msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
        msgBox.exec()