import webbrowser
from typing import Dict, Optional

from PIL import Image
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QWidget

from AppCore.ImageResource.ImageResourceDeployer import ImageResourceDeployer
from AppCore.Models import LocalAssetResource
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
        self._views: Dict[str, Optional[QWidget]] = {}

        menu_action_coordinator.bind_new_file(self.prompt_generate_new_file)
        menu_action_coordinator.bind_open_settings_page(self.open_settings_page)
        menu_action_coordinator.bind_open_about_page(self.open_about_page)
        menu_action_coordinator.bind_unstage_all_staging_resources(self.confirm_unstage_all_resources)
        menu_action_coordinator.bind_clear_cache_dir(self.confirm_clear_cache)
        menu_action_coordinator.bind_open_update_page(self.open_update_page)
        menu_action_coordinator.bind_open_shortcuts_page(self.open_shortcuts_page)
        menu_action_coordinator.bind_open_manage_deck_list_page(self.open_manage_deck_list_page)
        

    def prompt_generate_new_file(self):
        file_name, ok = QInputDialog.getText(None, 'Create new image file', 'Enter file name:')
        if ok:
            try:
                self._image_resource_deployer.generate_new_file(file_name, Image.open(self._asset_provider.image.swu_card_back))
                self._image_resource_deployer.load_production_resources()
            except Exception as error:
                self.show_error(error)

    def confirm_unstage_all_resources(self):
        if self.prompt_accept("Unstage all staged resources", "Are you sure you want to unstage all staged resources?"):
            self._image_resource_deployer.unstage_all_resources()

    def confirm_clear_cache(self):
        if self.prompt_accept("Clear cache", "Are you sure you want to clear the cache?"):
            self._platform_service_provider.platform_service.clear_cache()
    
    def prompt_accept(self, title: str, message: str) -> bool:
        dlg = QMessageBox()
        dlg.setWindowTitle(title)
        dlg.setText(message)
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) # type: ignore
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()
        return button == QMessageBox.StandardButton.Yes

    def open_settings_page(self):
        view = self._component_provider.settings_view
        self._open_view("settings", view)

    def open_about_page(self):
        view = self._component_provider.about_view
        self._open_view("about", view)
            
    def open_shortcuts_page(self):
        view = self._component_provider.shortcuts_view
        self._open_view("shortcuts", view)
    
    def open_manage_deck_list_page(self):
        view = self._component_provider.manage_deck_list_view
        self._open_view("manage_deck_list", view)
    
    def open_locally_managed_deck_preview(self, resource: LocalAssetResource):        
        view = self._component_provider.locally_managed_deck_preview_view(resource)
        self._open_view(resource.asset_path, view)
    
    def _open_view(self, object_name: str, view: QWidget):
        def remove_ref():
            self._views[object_name] = None
        if object_name in self._views:
            obj = self._views[object_name]
            if obj is not None:
            # Window already exists, activate it
                obj.show()
                obj.activateWindow()
                obj.raise_()
                if obj.isMinimized():
                    obj.showNormal()
                return
        
        view.setObjectName(object_name)
        view.destroyed.connect(remove_ref)
        view.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self._views[object_name] = view
        view.show()
    
    def show_error(self, error: Exception):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Icon.Critical)
        msgBox.setText(str(error))
        msgBox.setWindowTitle("Error")
        msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
        msgBox.exec()
        
    def open_update_page(self):
        webbrowser.open("https://github.com/hdchan/R4-MG/releases/latest")