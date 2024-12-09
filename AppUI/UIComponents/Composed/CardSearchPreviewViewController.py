
from typing import List

from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QSizePolicy,
                             QVBoxLayout, QWidget)

from AppCore.Data.CardSearchDataSource import CardSearchDataSource
from AppCore.Image.ImageResourceProcessorProtocol import *
from AppCore.Models import LocalCardResource, SearchConfiguration, TradingCard
from AppCore.Observation import *
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        LocalResourceEvent)
from AppUI.AppDependencyProviding import AppDependencyProviding

from ..Base import ImagePreviewViewController, SearchTableView


class CardSearchPreviewViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 app_dependency_provider: AppDependencyProviding, 
                 card_search_data_source: CardSearchDataSource):
        super().__init__()
        self._observation_tower = app_dependency_provider.observation_tower
        self._card_search_source_provider = app_dependency_provider.api_client_provider
        self._card_image_source_provider = app_dependency_provider.image_source_provider
        self._card_search_data_source = card_search_data_source

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        # https://stackoverflow.com/a/19011496
        staging_view = ImagePreviewViewController(app_dependency_provider)
        staging_view.setMinimumHeight(300)
        staging_view.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.staging_view = staging_view
        layout.addWidget(staging_view)

        buttons_layout = QHBoxLayout()
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        layout.addWidget(buttons_widget)


        flip_button = QPushButton()
        flip_button.setText("Flip (Ctrl+F)")
        flip_button.setEnabled(False)
        flip_button.clicked.connect(self.tapped_flip_button)
        self.flip_button = flip_button
        buttons_layout.addWidget(flip_button)
        
        retry_button = QPushButton()
        retry_button.setText("Redownload")
        retry_button.setEnabled(False)
        retry_button.clicked.connect(self.tapped_retry_button)
        self.retry_button = retry_button
        buttons_layout.addWidget(retry_button)
        
        
        search_table_view = SearchTableView(app_dependency_provider)
        search_table_view.delegate = self
        self.search_table_view = search_table_view
        layout.addWidget(search_table_view, 2)
        
        search_source_label = QLabel()
        search_source_label.setOpenExternalLinks(True)
        layout.addWidget(search_source_label)
        self.search_source_label = search_source_label

        image_source_label = QLabel()
        image_source_label.setOpenExternalLinks(True)
        layout.addWidget(image_source_label)
        self.image_source_label = image_source_label

        self._load_source_labels()
        
        self._current_resource = None
        self._observation_tower.subscribe_multi(self, [LocalResourceEvent, 
                                                       ConfigurationUpdatedEvent])


    def tv_did_select(self, sv: SearchTableView, index: int):
        self._card_search_data_source.select_card_resource_for_card_selection(index)
        # TODO: need to set all staging button enabled
        # self.deployment_view.set_all_staging_button_enabled(True)

    def tv_did_tap_search(self, sv: SearchTableView, search_configuration: SearchConfiguration) -> None:
        self._card_search_data_source.search(search_configuration)

    def search(self):
        self.search_table_view.search()
        
    def search_leader(self):
        self.search_table_view.search_leader()
        
    def search_base(self):
        self.search_table_view.search_base()

    def set_search_focus(self):
        self.search_table_view.set_search_focus()

    def set_item_active(self, index: int):
        self.search_table_view.set_item_active(index)

    def set_image(self, is_flippable: bool, local_resource: LocalCardResource):
        self._current_resource = local_resource
        self.staging_view.set_image(local_resource)
        self.flip_button.setEnabled(is_flippable)
        # self.retry_button.setEnabled(local_resource.remote_image_url is not None)
        self._sync_retry_button()
        

    def update_list(self, result_list: List[TradingCard]):
        self.search_table_view.update_list(result_list)

    def tapped_flip_button(self):
        self._card_search_data_source.flip_current_previewed_card()
        
    def tapped_retry_button(self):
        self._card_search_data_source.redownload_currently_selected_card_resource()
    
    def _sync_retry_button(self):
        if self._current_resource is not None:
            self.retry_button.setEnabled(self._current_resource.remote_image_url is not None and not self._current_resource.is_loading)
        else:
            self.retry_button.setEnabled(False)
        
    
    def _load_source_labels(self):
        search_source_url = self._card_search_source_provider.client.site_source_url
        if 'https://' in search_source_url:
            self.search_source_label.setText(f'Search source: <a href="{search_source_url}">{search_source_url}</a>')
        else:
            self.search_source_label.setText(f'Search source: {search_source_url}')

        image_source_url = self._card_image_source_provider.card_image_source.site_source_url()
        self.image_source_label.setText(f'Image source: <a href="{image_source_url}">{image_source_url}</a>')
        
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == ConfigurationUpdatedEvent:
            self._load_source_labels()
        if type(event) == LocalResourceEvent:
            self._sync_retry_button()
                    