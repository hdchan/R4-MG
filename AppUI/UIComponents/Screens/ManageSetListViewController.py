from typing import List, Optional, Tuple

from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QSizePolicy

from AppCore.Models import LocalAssetResource
from AppCore.Observation import (TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import LocalAssetResourceFetchEvent
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from R4UI import (HorizontalBoxLayout, Label, LineEditText, PushButton,
                  RWidget, ScrollArea, VerticalBoxLayout)


class ManageSetListViewController(RWidget, TransmissionReceiverProtocol):
    
    class ListItemViewControllerDelegate:
        def did_delete(self) -> None:
            raise Exception
    
    class ListItemViewController(RWidget, TransmissionReceiverProtocol):
        
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
            
            self._text_edit = Label()
            self._preview = PushButton("Preview", self._did_click_preview)
            self._redownload = PushButton("Redownload", self._did_click_redownload)
            self._delete = PushButton("Delete", self._delete_deck)

            HorizontalBoxLayout([
                self._text_edit,
                self._preview,
                self._redownload,
                self._delete
            ]).set_layout_to_widget(self)

            self._sync_ui()
            
            self._observation_tower.subscribe(self, LocalAssetResourceFetchEvent)
        
        def _sync_ui(self):
            self._redownload.setEnabled(self._resource.is_ready)
            self._delete.setEnabled(self._resource.is_ready)
            self._preview.setEnabled(self._resource.is_ready)
            
            if self._resource.is_loading:
                # TODO: force delete if temp still persistent?
                # TODO: add data last modified label
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
            if type(event) is LocalAssetResourceFetchEvent:
                if event.local_resource == self._resource:
                    self._sync_ui()
    
    class AddListItemViewControllerDelegate:
        def did_save(self) -> None:
            raise NotImplementedError
    
    

    class AddListItemViewController(RWidget):
        class Validator(QValidator):
            def validate(self, a0: Optional[str], a1: int) -> Tuple['QValidator.State', str, int]:
                # TODO: Assuming alphanumeric chars. Might want to abstract this to client level
                if a0 is None:
                    return (QValidator.State.Invalid, a0 if a0 is not None else '', a1)
                result = ''.join([char for char in a0 if char.isalnum()])
                return (QValidator.State.Acceptable, result, len(result))
            
        def __init__(self, 
                     app_dependencies_provider: AppDependenciesInternalProviding, delegate: Optional['ManageSetListViewController'.AddListItemViewControllerDelegate] = None):
            super().__init__()
            self._set_list_data_source = app_dependencies_provider.local_managed_sets_data_source
            self._asset_provider = app_dependencies_provider.asset_provider
            self.delegate: Optional[ManageSetListViewController.AddListItemViewControllerDelegate] = delegate
            
            helper_text = "Enter set identifier below to save and download a deck to use for locally managed set search. These identifiers can be found on the bottom right of a card within its set."

            self._text_edit = LineEditText(triggered_fn=self._text_edit_text_changed, placeholder_text='e.g. "SOR" for Spark of the Rebellion')

            self._save_download = PushButton("Save", self._add_and_download)

            VerticalBoxLayout([
                Label(helper_text).set_word_wrap(True),
                HorizontalBoxLayout([
                    self._text_edit,
                    self._save_download
                ]),
                PushButton("Rebuild database", self._rebuild_db)
            ]).set_layout_to_widget(self)

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

        def _rebuild_db(self):
            self._set_list_data_source.rebuild_locally_managed_sets_db()
    
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        self._set_list_data_source = app_dependencies_provider.local_managed_sets_data_source
        self._configuration_manager = app_dependencies_provider.configuration_manager
        self._app_dependencies_provider = app_dependencies_provider
        self._observation_tower = app_dependencies_provider.observation_tower
        
        self.setWindowTitle("Manage set list")
        self.setMinimumSize(400, 400)
        
        cells_container_widget = RWidget()
        cells_container_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed) # prevent stretching of container in scroll view
        self._cells_container_layout = VerticalBoxLayout([
            
        ]).set_uniform_content_margins(0).set_layout_to_widget(cells_container_widget)

        VerticalBoxLayout([
            ScrollArea(cells_container_widget),
            self.AddListItemViewController(self._app_dependencies_provider, self)
        ]).set_layout_to_widget(self)

        self._load_set_list()
      
    def _load_set_list(self):
        widgets: List[RWidget] = []
        for resource in self._set_list_data_source.deck_resources:
            row = self.ListItemViewController(self._app_dependencies_provider, resource)
            row.delegate = self
            widgets.append(row)
        self._cells_container_layout.replace_all_widgets(widgets)
            
    def _sync_ui(self):
        self._load_set_list()
        
    def did_save(self):
        self._sync_ui()
        
    def did_delete(self):
        self._sync_ui()