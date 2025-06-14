from PyQt5.QtWidgets import QSizePolicy, QTabWidget, QVBoxLayout, QWidget

from AppCore.Data.RecentPublishedDataSource import RecentPublishedDataSource
from AppCore.Data.RecentSearchDataSource import RecentSearchDataSource
from AppCore.Image.ImageResourceProcessorProtocol import *
from AppCore.Observation import *
from AppCore.Observation.Events import ConfigurationUpdatedEvent, SearchEvent
from AppUI.AppDependencyProviding import AppDependencyProviding

from ..Base import (CustomDirectorySearchTableViewController,
                    ImagePreviewViewController,
                    PublishHistoryTableViewController,
                    SearchHistoryTableViewController,
                    SearchTableViewController)


class CardSearchPreviewViewController(QWidget, TransmissionReceiverProtocol):
    class TabKeys:
        CUSTOM_DIR_SEARCH = 0
        CARD_SEARCH = 1
        PUBLISH_HISTORY = 2
        SEARCH_HISTORY = 3
        
    def __init__(self, 
                 app_dependency_provider: AppDependencyProviding,
                 recent_published_data_source: RecentPublishedDataSource,
                 recent_search_data_source: RecentSearchDataSource,
                 image_preview_view: ImagePreviewViewController):
        super().__init__()
        self._observation_tower = app_dependency_provider.observation_tower
        self._recent_published_data_source = recent_published_data_source
        self._recent_search_data_source = recent_search_data_source
        self._shortcut_action_coordinator = app_dependency_provider.shortcut_action_coordinator

        containing_layout = QVBoxLayout()
        containing_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(containing_layout)

        # https://stackoverflow.com/a/19011496
        # image_preview_view.setMinimumHeight(360)
        image_preview_view.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        containing_layout.addWidget(image_preview_view)

        self._tab_widget = QTabWidget()
        self._tab_widget.currentChanged.connect(self.on_tab_changed)
        containing_layout.addWidget(self._tab_widget, 2)
        
        
        self._custom_dir_search_table_view = CustomDirectorySearchTableViewController(app_dependency_provider, 
                                                                                      image_preview_view)
        self._tab_widget.addTab(self._custom_dir_search_table_view, "Custom Dir")
        
        
        self._search_table_view = SearchTableViewController(app_dependency_provider,
                                                            image_preview_view)
        
        self._tab_widget.addTab(self._search_table_view, "Card Search")
        
        
        self._publish_history_list = PublishHistoryTableViewController(app_dependency_provider, 
                                                                       recent_published_data_source, 
                                                                       image_preview_view)
        self._tab_widget.addTab(self._publish_history_list, "Publish History")

        self._search_history_list = SearchHistoryTableViewController(app_dependency_provider,
                                                                     recent_search_data_source, 
                                                                     self._search_table_view.card_search_data_source)
        self._tab_widget.addTab(self._search_history_list, "Search History")
        
        self._observation_tower.subscribe_multi(self, [SearchEvent, ConfigurationUpdatedEvent])

    def on_tab_changed(self, index: int):
        if index == CardSearchPreviewViewController.TabKeys.CARD_SEARCH:
            self._search_table_view.set_active()
        elif index == CardSearchPreviewViewController.TabKeys.CUSTOM_DIR_SEARCH:
            self._custom_dir_search_table_view.set_active()
        elif index == CardSearchPreviewViewController.TabKeys.PUBLISH_HISTORY:
            self._publish_history_list.set_active()
        elif index == CardSearchPreviewViewController.TabKeys.SEARCH_HISTORY:
            self._search_history_list.set_active()

    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == SearchEvent:
            if event.event_type == SearchEvent.EventType.STARTED and event.source_type == SearchEvent.SourceType.REMOTE:
                self._tab_widget.setCurrentIndex(CardSearchPreviewViewController.TabKeys.CARD_SEARCH)
        if type(event) == ConfigurationUpdatedEvent:
            if self._tab_widget.currentIndex() == CardSearchPreviewViewController.TabKeys.CARD_SEARCH:
                self._search_table_view.get_selection()

    