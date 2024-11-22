
from typing import List

from PyQt5.QtWidgets import (QLabel, QPushButton, QSizePolicy, QVBoxLayout,
                             QWidget)

from AppCore.Config import ConfigurationProvider
from AppCore.Models import CardType, TradingCard
from AppCore.Observation import ObservationTower
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        LocalResourceEvent,
                                        TransmissionProtocol)
from AppCore.Resource import CardImageSourceProviderProtocol
from AppCore.Models import LocalCardResource
from ..Base import ImagePreviewViewController, SearchTableView


class CardSearchPreviewViewController(QWidget):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 configuration_provider: ConfigurationProvider, 
                 card_type_list: List[CardType], 
                 card_image_source_provider: CardImageSourceProviderProtocol):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)
        self._observation_tower = observation_tower
        self._card_image_source_provider = card_image_source_provider
        # https://stackoverflow.com/a/19011496
        preview_view = ImagePreviewViewController(observation_tower, 
                                                  configuration_provider)
        preview_view.delegate = self
        preview_view.setMinimumHeight(300)
        
        self.staging_view = preview_view
        preview_view.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        # lbl2.setMinimumHeight(300);
        layout.addWidget(preview_view)

        retry_button = QPushButton()
        retry_button.setText("Redownload")
        # retry_button.setEnabled(False)
        retry_button.clicked.connect(self.tapped_retry_button)
        self.retry_button = retry_button
        layout.addWidget(retry_button)

        flip_button = QPushButton()
        flip_button.setText("Flip (Ctrl+F)")
        flip_button.setEnabled(False)
        flip_button.clicked.connect(self.tapped_flip_button)
        self.flip_button = flip_button
        layout.addWidget(flip_button)
        
        search_table_view = SearchTableView(observation_tower, 
                                            card_type_list)
        search_table_view.delegate = self
        self.search_table_view = search_table_view
        layout.addWidget(search_table_view)
        
        image_source_label = QLabel()
        image_source_label.setOpenExternalLinks(True)
        layout.addWidget(image_source_label)
        self.image_source_label = image_source_label
        self._load_image_source_label()
        
        self._current_image_path = None
        self._observation_tower.subscribe_multi(self, [LocalResourceEvent, 
                                                       ConfigurationUpdatedEvent])

    @property
    def delegate(self):
        return self._delegate
    
    @delegate.setter
    def delegate(self, value):
        self._delegate = value
        self.search_table_view.delegate = value
        self.staging_view.delgate = value

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
        self._current_image_path = local_resource.image_preview_path
        self.staging_view.set_image(local_resource)
        self.flip_button.setEnabled(is_flippable)
        

    def update_list(self, result_list: List[TradingCard]):
        self.search_table_view.update_list(result_list)

    def tapped_flip_button(self):
        self.delegate.cs_did_tap_flip_button(self)
        
    def tapped_retry_button(self):
        self.delegate.cs_did_tap_retry_button(self)
        
    def _load_image_source_label(self):
        url = self._card_image_source_provider.provideSource().site_source_url()
        self.image_source_label.setText(f'Image source: <a href="{url}">{url}</a>')
        
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == LocalResourceEvent:
            if self._current_image_path is not None:
                pass
        elif type(event) == ConfigurationUpdatedEvent:
            self._load_image_source_label()
                # if self._current_image_path == event.local_resource.image_preview_path:
                #     if event.event_type == LocalResourceEvent.EventType.STARTED:
                #         self.retry_button.setEnabled(False)
                #     elif event.event_type == LocalResourceEvent.EventType.FINISHED:
                #         self.retry_button.setEnabled(True)
                    