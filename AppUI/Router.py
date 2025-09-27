import webbrowser
from typing import Dict, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QWidget

from AppCore.CoreDependenciesInternalProviding import \
    CoreDependenciesInternalProviding
from AppCore.DataSource.DataSourceImageResourceDeployer import DataSourceImageResourceDeployer
from AppCore.Models import LocalAssetResource, LocalCardResource, LocalResourceDraftListWindow
from AppUI.ScreenWidgetProviding import ScreenWidgetProviding


class Router:
    def __init__(self,
                 core_dependencies_internal_provider: CoreDependenciesInternalProviding, 
                 data_source_image_resource_deployer: DataSourceImageResourceDeployer, 
                 component_provider: ScreenWidgetProviding):
        self._data_source_image_resource_deployer = data_source_image_resource_deployer
        self._component_provider = component_provider
        self._platform_service_provider = core_dependencies_internal_provider.platform_service_provider
        self._data_source_draft_list = core_dependencies_internal_provider.data_source_draft_list
        self._views: Dict[str, Optional[QWidget]] = {}
    
    def close_all_child_views(self):
        for v in self._views.values():
            if v is not None:
                v.close()
        self._views = {}

    def prompt_generate_new_file_with_placeholder(self, placeholder_image_path: Optional[str]):
        file_name, ok = QInputDialog.getText(None, 'Create new image file', 'Enter file name:')
        if ok:
            try:
                self._data_source_image_resource_deployer.generate_new_file(file_name, placeholder_image_path)
                self._data_source_image_resource_deployer.load_production_resources()
            except Exception as error:
                self.show_error(error)
                
    # def prompt_rename_draft_list_pack(self, pack_index: int):
    #     pack_name, ok = QInputDialog.getText(None, 'Rename', 'Enter pack name:')
    #     if ok:
    #         self._data_source_draft_list.update_pack_name(pack_index, pack_name)
            
    def prompt_text_input(self, title: str, description: str) -> tuple[str, Optional[bool]]:
        return QInputDialog.getText(None, title, description)
    
    def confirm_unstage_all_resources(self):
        if self.prompt_accept("Unstage all staged resources", "Are you sure you want to unstage all staged resources?"):
            self._data_source_image_resource_deployer.unstage_all_resources()

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
        
    def open_app_settings_page(self):
        view = self._component_provider.app_settings_view
        self._open_view("app_settings", view)
        
    def open_draft_list_settings_page(self):
        view = self._component_provider.draft_list_settings_view()
        self._open_view("draft_list_settings", view)

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
    
    def open_draft_list_standalone_view(self, resource: LocalResourceDraftListWindow):
        view = self._component_provider.draft_list_standalone_view(resource)
        self._open_view(f'{resource.asset_path}', view)
    
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
    
    def open_link_to_card_resource(self, local_resource: LocalCardResource):
        if local_resource.remote_image_url is not None:
            webbrowser.open(local_resource.remote_image_url)
    
    def open_update_page(self):
        webbrowser.open("https://github.com/hdchan/R4-MG/releases/latest")