from PyQt5.QtWidgets import QSizePolicy, QTabWidget, QVBoxLayout, QWidget

from AppCore.Data.CardSearchDataSource import CardSearchDataSource
from AppCore.Data.RecentPublishedDataSource import RecentPublishedDataSource
from AppCore.Image.ImageResourceProcessorProtocol import *
from AppCore.Observation import *
from AppUI.AppDependencyProviding import AppDependencyProviding

from ..Base import (ImagePreviewViewController,
                    PublishHistoryTableViewController,
                    SearchTableViewController)


class CardSearchPreviewViewController(QWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 app_dependency_provider: AppDependencyProviding, 
                 card_search_data_source: CardSearchDataSource, 
                 recent_published_data_source: RecentPublishedDataSource):
        super().__init__()
        self._observation_tower = app_dependency_provider.observation_tower
        
        self._card_search_data_source = card_search_data_source
        
        self._recent_published_data_source = recent_published_data_source

        containing_layout = QVBoxLayout()
        containing_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(containing_layout)

        # https://stackoverflow.com/a/19011496
        image_preview_view = ImagePreviewViewController(app_dependency_provider)
        image_preview_view.setMinimumHeight(300)
        image_preview_view.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        containing_layout.addWidget(image_preview_view)

        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        containing_layout.addWidget(self.tabs, 2)
        
        self._search_table_view = SearchTableViewController(app_dependency_provider,
                                                            card_search_data_source, 
                                                            image_preview_view)
        self.tabs.addTab(self._search_table_view, "Search")
        
        self._history_list = PublishHistoryTableViewController(app_dependency_provider, 
                                                               recent_published_data_source, 
                                                               image_preview_view)
        self.tabs.addTab(self._history_list, "Publish History")

    def on_tab_changed(self, index: int):
        if index == 0:
            self._search_table_view.set_active()
        elif index == 1:
            self._history_list.set_active()

    def search(self):
        self._search_table_view.search()
        
    def search_leader(self):
        self._search_table_view.search_leader()
        
    def search_base(self):
        self._search_table_view.search_base()

    def set_search_focus(self):
        self._search_table_view.set_search_focus()

    def set_item_active(self, index: int):
        self._search_table_view.set_item_active(index)