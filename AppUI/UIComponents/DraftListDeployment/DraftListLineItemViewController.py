import weakref
from typing import List, Optional
from weakref import ReferenceType

from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QAction, QMenu, QWidget, QVBoxLayout, QLabel

from AppCore.DataSource import LocalResourceDataSourceProviding
from AppCore.Models import LocalCardResource, TradingCard, DraftPack
from AppUI.AppDependenciesProviding import AppDependenciesProviding

from AppUI.Models.DraftListStyleSheet import DraftListStyleSheet


class DraftListLineItemViewControllerDelegate:
    @property
    def dlli_can_edit(self) -> bool:
        return True

class DraftListLineItemViewController(QWidget):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesProviding,
                 stylesheet: DraftListStyleSheet, # TODO: move style sheet to client side
                 trading_card: TradingCard,
                 local_resource: LocalCardResource, # Able to access resource without checking optional trading card
                 data_source_local_resource_provider: Optional[LocalResourceDataSourceProviding],
                 pack_index: int, 
                 draft_pack: DraftPack,
                 card_index: int):
        super().__init__()
        self._stylesheet = stylesheet
        self._asset_provider = app_dependencies_provider.asset_provider
        self._data_source_draft_list = app_dependencies_provider.data_source_draft_list
        self._data_source_local_resource_provider = data_source_local_resource_provider
        self._data_source_image_resource_deployer = app_dependencies_provider.data_source_image_resource_deployer
        self._router = app_dependencies_provider.router
        self._trading_card = trading_card
        self._local_resource = local_resource
        self._pack_index = pack_index
        self._draft_pack = draft_pack
        self._card_index = card_index
        self._external_app_dependencies_provider = app_dependencies_provider.external_app_dependencies_provider
        self._delegate: Optional[ReferenceType[DraftListLineItemViewControllerDelegate]] = None
        
        self._setup_view()
    
    def set_delegate(self, delegate: DraftListLineItemViewControllerDelegate):
        self._delegate = weakref.ref(delegate)
    
    def _setup_view(self):
        container_layout = QVBoxLayout()
        self.setLayout(container_layout)
        # TODO: set transparent?
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        external_list_item = self._external_app_dependencies_provider.draft_list_item_cell(self._trading_card, 
                                                                                           self._pack_index, 
                                                                                           self._card_index, 
                                                                                           self._stylesheet)
        
        if external_list_item is not None:
            container_layout.addWidget(external_list_item)
        else:
            # default cell
            label = QLabel()
            label.setText(self._trading_card.name)
            container_layout.addWidget(label)
        
    def contextMenuEvent(self, a0: Optional[QContextMenuEvent]):
        
        if self._delegate is not None:
            delegate = self._delegate()
            if delegate is not None:
                if not delegate.dlli_can_edit:
                    return
        
        trading_card = self._trading_card
        
        context_menu = QMenu(self)

        delete_action = QAction(f"Delete - {trading_card.name}", self)
        delete_action.triggered.connect(lambda: self._delete_card(trading_card))
        context_menu.addAction(delete_action) # type: ignore
        
        context_menu.addSeparator()
        
        move_up_action = QAction(f"Move Up - {trading_card.name}", self)
        move_up_action.triggered.connect(lambda: self._data_source_draft_list.move_up(self._pack_index, self._card_index))
        context_menu.addAction(move_up_action) # type: ignore
        
        move_down_action = QAction(f"Move Down - {trading_card.name}", self)
        move_down_action.triggered.connect(lambda: self._data_source_draft_list.move_down(self._pack_index, self._card_index))
        context_menu.addAction(move_down_action) # type: ignore
        
        
        if self._data_source_local_resource_provider is not None:
            selected_resource = self._data_source_local_resource_provider.data_source.selected_local_resource
        
            if selected_resource is not None:
                context_menu.addSeparator()
                
                insert_above_action = QAction(f"Insert Above - {trading_card.name}", self)
                insert_above_action.triggered.connect(lambda: self._data_source_draft_list.insert_above(self._pack_index, self._card_index, selected_resource))
                context_menu.addAction(insert_above_action) # type: ignore
                
                insert_below_action = QAction(f"Insert Below - {trading_card.name}", self)
                insert_below_action.triggered.connect(lambda: self._data_source_draft_list.insert_below(self._pack_index, self._card_index, selected_resource))
                context_menu.addAction(insert_below_action) # type: ignore

        deployment_resources = self._data_source_image_resource_deployer.deployment_resources
        deployment_actions: List[QAction] = []
        if len(deployment_resources) > 0:
            context_menu.addSeparator()
            for d in deployment_resources:
                name = d.production_resource.file_name_with_ext
                action = QAction(f"Stage to - {name}", self)
                action.triggered.connect(lambda _, deployment_resource=d: # type: ignore
                    self._data_source_image_resource_deployer.stage_resource(deployment_resource, self._local_resource)) # type: ignore
                deployment_actions.append(action)
                context_menu.addAction(action) # type: ignore

        if a0 is not None:
            context_menu.exec_(a0.globalPos())
                
    def _delete_card(self, trading_card: TradingCard):
        if self._router.prompt_accept(f"Delete {trading_card.name}?", f"Are you sure you want to delete {trading_card.name}"):
            self._data_source_draft_list.remove_resource(self._pack_index, self._card_index)