from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPalette, QPixmap, QResizeEvent
from PyQt5.QtWidgets import (QFrame, QScrollArea, QSizePolicy, QSpacerItem,
                             QVBoxLayout, QWidget)

from AppCore.DataSource import LocalResourceDataSourceProviding
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        DraftListUpdatedEvent)
from AppCore.Observation.ObservationTower import *
from AppUI.AppDependenciesProviding import AppDependenciesProviding
from AppUI.Models.DraftListStyleSheet import DraftListStyleSheet
from PyQtUI import VerticalBoxLayout, VerticallyExpandingSpacer

from .DraftListLineItemHeaderViewController import \
    DraftListLineItemHeaderViewController
from .DraftListLineItemViewController import (
    DraftListLineItemViewController, DraftListLineItemViewControllerDelegate)


class DraftListTablePackPreviewViewControllerDelegate:    
    @property
    def dlp_pack_identifier(self) -> Optional[str]:
        return None
    
    @property
    def dlp_is_staging_view(self) -> bool:
        return True

class DraftListTablePackPreviewViewController(QWidget, TransmissionReceiverProtocol, DraftListLineItemViewControllerDelegate):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesProviding, 
                 data_source_local_resource_provider: Optional[LocalResourceDataSourceProviding]):
        super().__init__()
        self._app_dependencies_provider = app_dependencies_provider
        self._data_source_draft_list = app_dependencies_provider.data_source_draft_list
        self._data_source_local_resource_provider = data_source_local_resource_provider
        self._app_ui_configuration_manager = app_dependencies_provider.app_ui_configuration_manager
        self._external_app_dependencies_provider = app_dependencies_provider.external_app_dependencies_provider
        self._delegate: Optional[DraftListTablePackPreviewViewControllerDelegate] = None
        self._setup_view()
        
        app_dependencies_provider.observation_tower.subscribe_multi(self, [ConfigurationUpdatedEvent,
                                                                           DraftListUpdatedEvent])
    
    
    @property
    def _stylesheet(self) -> DraftListStyleSheet:
        return self._app_ui_configuration_manager.configuration.draft_list_styles
    
    @property
    def delegate(self) -> Optional[DraftListTablePackPreviewViewControllerDelegate]:
        return self._delegate
    
    @delegate.setter
    def delegate(self, delegate: DraftListTablePackPreviewViewControllerDelegate):
        self._delegate = delegate
        self._sync_ui()
    
    def _setup_view(self):
        outer_container_layout = QVBoxLayout()
        outer_container_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(outer_container_layout)
        
        # self.setContentsMargins(0, 0, 0, 0)
        # cells_container_layout = QVBoxLayout()
        # cells_container_widget = QWidget()
        # the below code was causing line item to get squashed, adding a spacer below all line items
        # cells_container_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed) # prevent stretching of container in scroll view
        # cells_container_widget.setLayout(cells_container_layout)
        # self._cells_container_layout = cells_container_layout
        # self._cells_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self._cells_container = VerticalBoxLayout().set_uniform_content_margins(0)
        
        self._cells_container_container = VerticalBoxLayout([
            self._cells_container
        ]).set_uniform_content_margins(0).add_spacer(VerticallyExpandingSpacer())
        
        self._scroll_view = QScrollArea(self)
        self._scroll_view.setFrameShape(QFrame.Shape.NoFrame)
        
        self._scroll_view.setWidget(self._cells_container_container)
        self._scroll_view.setWidgetResizable(True)
        outer_container_layout.addWidget(self._scroll_view)
        
        self._sync_ui()
    
    def clear_list(self):
        self._cells_container.replace_all_widgets([])
        # for i in reversed(range(self._cells_container_layout.count())):
        #     layout_item = self._cells_container_layout.takeAt(i)
        #     if layout_item is not None:
        #         widget = layout_item.widget()
        #         if widget is not None:
        #             widget.deleteLater()
        #             widget = None
    
    def _sync_list(self):
        vertical_scroll_bar = self._scroll_view.verticalScrollBar()
        current_v_pos = 0
        if vertical_scroll_bar is not None:
            current_v_pos = vertical_scroll_bar.value()
        
        self.clear_list()
        if self._delegate is not None and self._delegate.dlp_pack_identifier is not None:
            pack_identifier = self._delegate.dlp_pack_identifier
            aggregate_list: bool = not self._delegate.dlp_is_staging_view and self._stylesheet.is_list_aggregated
            
            draft_pack = self._data_source_draft_list.pack_for_draft_pack_identifier(pack_identifier)
            if draft_pack is None:
                return
            list_to_enumerate = draft_pack.draft_list
            externally_modified_list = self._external_app_dependencies_provider.draft_resource_list(list_to_enumerate, aggregate_list)
            if externally_modified_list is not None:
                list_to_enumerate = externally_modified_list # use external implementation if present
            
            pack_name = draft_pack.pack_name
            if pack_name:
                self._cells_container.add_widget(DraftListLineItemHeaderViewController(self._app_dependencies_provider, self._stylesheet, pack_name))
            
            for (card_index, local_resource) in enumerate(list_to_enumerate):
                trading_card = local_resource.trading_card
                if trading_card is None:
                    continue
                pack_index = self._data_source_draft_list.pack_index_for_draft_pack_identifier(pack_identifier)
                if pack_index is None:
                    continue
                line_item = DraftListLineItemViewController(self._app_dependencies_provider,
                                                            self._stylesheet,
                                                            trading_card,
                                                            local_resource,
                                                            self._data_source_local_resource_provider,
                                                            pack_index,
                                                            draft_pack,
                                                            card_index)
                line_item.set_delegate(self)
                self._cells_container.add_widget(line_item)
            
                
        if vertical_scroll_bar is not None:
            # TODO: need to fix
            min_position = min(vertical_scroll_bar.maximum(), current_v_pos)
            vertical_scroll_bar.setValue(min_position)
    
    def _sync_styles(self):
        stylesheet = self._stylesheet
        self.setContentsMargins(stylesheet.container_padding_left, 
                                stylesheet.container_padding_top, 
                                stylesheet.container_padding_right, 
                                stylesheet.container_padding_bottom)
        
        self._cells_container.set_spacing(stylesheet.cell_spacing)
        
        if self.delegate is not None and not self.delegate.dlp_is_staging_view:
            self._scroll_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            
        palette = self.palette()
        # background_image = self._stylesheet.container_background_image_path
        background_image = None
        if background_image is not None:
            pixmap = QPixmap(background_image)
        
            height = self.height()
            width = self.width()
            scaled_pixmap = pixmap.scaled(
                    width, height, 
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation
                )
            palette.setBrush(QPalette.ColorRole.Window, QBrush(scaled_pixmap))
        else:
            palette.setColor(QPalette.ColorRole.Background, QColor(stylesheet.container_background_color)) # Set background color
            
        self.setAutoFillBackground(True) # Enable background filling
        self.setPalette(palette)
    
    # MARK: - DraftListLineItemViewControllerDelegate
    @property
    def dlli_can_edit(self) -> bool:
        if self.delegate is not None:
            return self.delegate.dlp_is_staging_view
        return True
    
    def sync_ui(self):
        self._sync_ui()
    
    def _sync_ui(self):
        self._sync_list()
        self._sync_styles()
       
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == ConfigurationUpdatedEvent:
            # TODO: needs to optimize?
            self._sync_ui()
            
        if type(event) == DraftListUpdatedEvent:
            self._sync_ui()
            return
            if self._delegate is not None:
                if event.draft_pack.pack_identifier == self._delegate.dlp_pack_identifier:
                    # self._sync_ui()
                    event_type = event.event_type
                    draft_pack = event.draft_pack
                    if type(event_type) == DraftListUpdatedEvent.AddedResource:
                        trading_card = event_type.local_resource.trading_card
                        pack_index = self._data_source_draft_list.pack_index_for_draft_pack_identifier(draft_pack.pack_identifier)
                        
                        if trading_card is None or pack_index is None:
                            return
                        
                        line_item = DraftListLineItemViewController(self._app_dependencies_provider,
                                                                    self._stylesheet,
                                                                    trading_card,
                                                                    event_type.local_resource,
                                                                    self._data_source_local_resource_provider,
                                                                    pack_index,
                                                                    draft_pack,
                                                                    event_type.index)
                        
                        self._cells_container.add_widget(line_item)
                        
                    elif type(event_type) == DraftListUpdatedEvent.SwappedResources:
                        self._cells_container.swap_widgets(event_type.index_1, event_type.index_2)
                    
                    elif type(event_type) == DraftListUpdatedEvent.RemovedResource:
                        self._cells_container.remove_widget_at_index(event_type.index)
                    
                    elif type(event_type) == DraftListUpdatedEvent.InsertedResource:
                        trading_card = event_type.local_resource.trading_card
                        pack_index = self._data_source_draft_list.pack_index_for_draft_pack_identifier(draft_pack.pack_identifier)
                        
                        if trading_card is None or pack_index is None:
                            return
                        
                        line_item = DraftListLineItemViewController(self._app_dependencies_provider,
                                                                    self._stylesheet,
                                                                    trading_card,
                                                                    event_type.local_resource,
                                                                    self._data_source_local_resource_provider,
                                                                    pack_index,
                                                                    draft_pack,
                                                                    event_type.index)
                        self._cells_container.insert_widget(event_type.index, line_item)
                    # TODO: make only necessary updates to table, get more granular changes from DS event
                
            
    # def resizeEvent(self, a0: Optional[QResizeEvent]):
    # needed for background image?
    #     # must use event value here to get size
    #     self._sync_styles()
    #     if a0 is not None:
    #         super(DraftListTablePackPreviewViewController, self).resizeEvent(a0)