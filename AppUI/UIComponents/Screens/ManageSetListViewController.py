from typing import Optional, Tuple
from PyQt5.QtGui import QPixmap, QValidator
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QScrollArea, QSizePolicy, QVBoxLayout, QWidget)

from AppCore.Models import LocalAssetResource
from AppCore.Observation import (TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import LocalAssetResourceFetchEvent
from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding


class ManageSetListViewController(QWidget, TransmissionReceiverProtocol):
    
    class ListItemViewControllerDelegate:
        def did_delete(self) -> None:
            raise Exception
    
    class ListItemViewController(QWidget, TransmissionReceiverProtocol):
        
        def __init__(self, 
                     app_dependencies_provider: AppDependenciesInternalProviding, 
                     resource: LocalAssetResource):
            super().__init__()
            self._set_list_data_source = app_dependencies_provider.local_managed_sets_data_source
            self._configuration_manager = app_dependencies_provider.configuration_manager
            self._observation_tower = app_dependencies_provider.observation_tower
            self._router = app_dependencies_provider.router
            self._resource = resource
            self.delegate: Optional[ManageSetListViewController.ListItemViewControllerDelegate] = None
            
            v_layout = QHBoxLayout()
            self.setLayout(v_layout)
            
            text_edit = QLabel()
            v_layout.addWidget(text_edit)
            self._text_edit = text_edit
            
            preview = QPushButton()
            preview.setText("Preview")
            preview.clicked.connect(self._did_click_preview)
            v_layout.addWidget(preview)
            self._preview = preview
            
            redownload = QPushButton()
            redownload.setText("Redownload")
            redownload.clicked.connect(self._did_click_redownload)
            v_layout.addWidget(redownload)
            self._redownload = redownload
            
            delete = QPushButton()
            delete.setText("Delete")
            delete.clicked.connect(self._delete_deck)
            v_layout.addWidget(delete)
            self._delete = delete

            self._sync_ui()
            
            self._observation_tower.subscribe(self, LocalAssetResourceFetchEvent)
        
        def _sync_ui(self):
            self._redownload.setEnabled(self._resource.is_ready)
            self._delete.setEnabled(self._resource.is_ready)
            self._preview.setEnabled(self._resource.is_ready)
            
            if self._resource.is_loading:
                # TODO: force delete if temp still persistent?
                self._text_edit.setText(f'{self._resource.display_name.upper()} (installing...)')
            elif self._resource.is_ready:
                self._text_edit.setText(f'{self._resource.display_name.upper()} (installed)')
            else:
                self._text_edit.setText(f'{self._resource.display_name.upper()} (unknown)')
                
        def _did_click_redownload(self):
            if self._router.prompt_accept(f'Redownload {self._resource.display_name.upper()}', 
                                          f'Are you sure you want to download {self._resource.display_name.upper()} again?'):
                self._set_list_data_source.download(self._resource.display_name, force_download=True)
            
        def _delete_deck(self):
            if self._router.prompt_accept(f'Delete {self._resource.display_name.upper()}', 
                                          f'Are you sure you want to delete {self._resource.display_name.upper()}?'):
                self._set_list_data_source.remove(self._resource)
                if self.delegate is not None:
                    self.delegate.did_delete()
                    
        def _did_click_preview(self):    
            self._router.open_locally_managed_deck_preview(self._resource)
        
        def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
            if type(event) == LocalAssetResourceFetchEvent:
                if event.local_resource == self._resource:
                    self._sync_ui()
    
    class AddListItemViewControllerDelegate:
        def did_save(self) -> None:
            raise NotImplemented
    
    

    class AddListItemViewController(QWidget):
        class Validator(QValidator):
            def validate(self, a0: Optional[str], a1: int) -> Tuple['QValidator.State', str, int]:
                # TODO: Assuming alphanumeric chars. Might want to abstract this to client level
                if a0 is None:
                    return (QValidator.State.Invalid, a0 if a0 is not None else '', a1)
                result = ''.join([char for char in a0 if char.isalnum()])
                return (QValidator.State.Acceptable, result, len(result))
            
        def __init__(self, 
                     app_dependencies_provider: AppDependenciesInternalProviding):
            super().__init__()
            self._set_list_data_source = app_dependencies_provider.local_managed_sets_data_source
            self._asset_provider = app_dependencies_provider.asset_provider
            self.delegate: Optional[ManageSetListViewController.AddListItemViewControllerDelegate] = None
            
            v_layout = QVBoxLayout()
            self.setLayout(v_layout)
            
            helper_text = QLabel()
            helper_text.setWordWrap(True)
            helper_text.setText("Enter set identifier below to save and download a deck to use for locally managed set search. These identifiers can be found on the bottom right of a card within its set.")
            v_layout.addWidget(helper_text)
            
            h_layout = QHBoxLayout()
            h_layout_widget = QWidget()
            h_layout_widget.setLayout(h_layout)
            v_layout.addWidget(h_layout_widget)
            
            text_edit = QLineEdit()
            validator = self.Validator()
            text_edit.setValidator(validator)
            text_edit.textChanged.connect(self._text_edit_text_changed)
            text_edit.setPlaceholderText('e.g. "SOR" for Spark of the Rebellion')
            h_layout.addWidget(text_edit)
            self._text_edit = text_edit
            
            save_download = QPushButton()
            save_download.setText("Save")
            save_download.clicked.connect(self._add_and_download)
            h_layout.addWidget(save_download)
            self._save_download = save_download

            self._sync_save_button()
        
        def _add_and_download(self):
            # sanitize input
            self._set_list_data_source.download(self._text_edit.text())
            self._text_edit.clear()
            if self.delegate is not None:
                self.delegate.did_save()
        
        def _sync_save_button(self):
            stripped_text = self._text_edit.text().lower().strip()
            text_empty = not stripped_text
            existing_deck_identifiers = list(map(lambda resource: resource.display_name.lower(), self._set_list_data_source.deck_resources))
            self._save_download.setEnabled(not text_empty and stripped_text not in existing_deck_identifiers)
            
        def _text_edit_text_changed(self, new_text: str):

            self._sync_save_button()
    
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        self._set_list_data_source = app_dependencies_provider.local_managed_sets_data_source
        self._configuration_manager = app_dependencies_provider.configuration_manager
        self._app_dependencies_provider = app_dependencies_provider
        self._observation_tower = app_dependencies_provider.observation_tower
        
        self.setWindowTitle("Manage set list")
        self.setMinimumSize(400, 400)
        
        outer_container_layout = QVBoxLayout()
        self.setLayout(outer_container_layout)

        cells_container_layout = QVBoxLayout()
        cells_container_layout.setContentsMargins(0, 0, 0, 0)
        cells_container_widget = QWidget()
        cells_container_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed) # prevent stretching of container in scroll view
        cells_container_widget.setLayout(cells_container_layout)
        self._cells_container_layout = cells_container_layout

        self.scroll_view = QScrollArea(self)
        self.scroll_view.setWidget(cells_container_widget)
        self.scroll_view.setWidgetResizable(True)
        outer_container_layout.addWidget(self.scroll_view)
        
        add_list_item_row = self.AddListItemViewController(self._app_dependencies_provider)
        add_list_item_row.delegate = self
        outer_container_layout.addWidget(add_list_item_row)
        
        self._load_set_list()
    
    def _clear_list(self):
        for i in reversed(range(self._cells_container_layout.count())):
            layout_item = self._cells_container_layout.takeAt(i)
            if layout_item is not None:
                widget = layout_item.widget()
                if widget is not None:
                    widget.deleteLater()
      
    def _load_set_list(self):
        self._clear_list()
        for resource in self._set_list_data_source.deck_resources:
            row = self.ListItemViewController(self._app_dependencies_provider, resource)
            row.delegate = self
            self._cells_container_layout.addWidget(row)
            
    def _sync_ui(self):
        self._load_set_list()
        
    def did_save(self):
        self._sync_ui()
        
    def did_delete(self):
        self._sync_ui()