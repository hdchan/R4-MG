
from typing import List, Optional

from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QSizePolicy,
                             QVBoxLayout, QWidget)

from AppCore.Config import ConfigurationProviderProtocol
from AppCore.Data import APIClientProviderProtocol
from AppCore.Models import LocalCardResource, TradingCard
from AppCore.Observation import *
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        LocalResourceEvent)
from AppCore.Resource import CardImageSourceProviderProtocol

from ...Assets import AssetProvider
from ..Base import ImagePreviewViewController, SearchTableView


class CardSearchPreviewViewControllerDelegate:
    def cs_did_tap_flip_button(self, cs: ...) -> None:
        pass
    
    def cs_did_tap_retry_button(self, cs: ...) -> None:
        pass

class CardSearchPreviewViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 configuration_provider: ConfigurationProviderProtocol,
                 card_search_source_provider: APIClientProviderProtocol,
                 card_image_source_provider: CardImageSourceProviderProtocol, 
                 asset_provider: AssetProvider):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self._observation_tower = observation_tower
        self._card_search_source_provider = card_search_source_provider
        self._card_image_source_provider = card_image_source_provider
        # https://stackoverflow.com/a/19011496
        staging_view = ImagePreviewViewController(observation_tower, 
                                                  configuration_provider, 
                                                  asset_provider)
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
        
        
        search_table_view = SearchTableView(observation_tower,
                                            configuration_provider)
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

    @property
    def delegate(self) -> Optional[CardSearchPreviewViewControllerDelegate]:
        return self._delegate
    
    @delegate.setter
    def delegate(self, value: CardSearchPreviewViewControllerDelegate):
        self._delegate = value
        self.search_table_view.delegate = value
        self.staging_view.delegate = value

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
        if self.delegate is not None:
            self.delegate.cs_did_tap_flip_button(self)
        
    def tapped_retry_button(self):
        if self.delegate is not None:
            self.delegate.cs_did_tap_retry_button(self)
    
    def _sync_retry_button(self):
        if self._current_resource is not None:
            self.retry_button.setEnabled(self._current_resource.remote_image_url is not None and not self._current_resource.is_loading)
        else:
            self.retry_button.setEnabled(False)
        
    
    def _load_source_labels(self):
        search_source_url = self._card_search_source_provider.provideClient().site_source_url
        if 'https://' in search_source_url:
            self.search_source_label.setText(f'Search source: <a href="{search_source_url}">{search_source_url}</a>')
        else:
            self.search_source_label.setText(f'Search source: {search_source_url}')

        image_source_url = self._card_image_source_provider.provideSource().site_source_url()
        self.image_source_label.setText(f'Image source: <a href="{image_source_url}">{image_source_url}</a>')
        
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == ConfigurationUpdatedEvent:
            self._load_source_labels()
        if type(event) == LocalResourceEvent:
            self._sync_retry_button()
                    