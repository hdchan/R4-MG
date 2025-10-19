import webbrowser
from typing import Dict, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QWidget

from AppCore.Models import (LocalAssetResource, LocalCardResource,
                            LocalResourceDraftListWindow)
from AppUI.Router.ScreenWidgetProviding import ScreenWidgetProviding


class Router:
    def __init__(self, 
                 component_provider: ScreenWidgetProviding):
        self._component_provider = component_provider
        self._views: Dict[str, Optional[QWidget]] = {}
    
    def close_all_child_views(self):
        for v in self._views.values():
            if v is not None:
                v.close()
        self._views = {}
            
    def prompt_text_input(self, title: str, description: str) -> tuple[str, Optional[bool]]:
        return QInputDialog.getText(None, title, description)
    
    def prompt_accept(self, title: str, message: str) -> bool:
        dlg = QMessageBox()
        dlg.setWindowTitle(title)
        dlg.setText(message)
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) # type: ignore
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()
        return button == QMessageBox.StandardButton.Yes
        
    def open_app_settings_page(self):
        view = self._component_provider.app_settings_view
        self._open_view("app_settings", view)

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
    
    def open_image_deployment_view(self):
        view = self._component_provider.image_deployment_window()
        self._open_view("image_deployment", view)
        
    def open_draft_list_deployment_view(self):
        view = self._component_provider.draft_list_deployment_window()
        self._open_view("draft_list_deployment", view)
        
    def open_draft_list_image_preview_view(self):
        view = self._component_provider.draft_list_image_preview_view()
        self._open_view("draft_list_image_preview", view)
    
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