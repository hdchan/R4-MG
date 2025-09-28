
from typing import List, Optional

from PyQt5.QtWidgets import QWidget

from AppCore.DataSource import (DataSourceCardSearchClientProviding,
                                DataSourceLocallyManagedSets)
from AppCore.DataSource.DataSourceLocallyManagedSets import \
    DataSourceLocallyManagedSetsClientProtocol
from AppCore.Models import DraftPack, LocalCardResource, TradingCard
from AppUI.ExternalAppDependenciesProviding import *
from AppUI.Models import DraftListStyleSheet
from AppCore.DataSource import DataSourceDraftList

class ExternalAppDependenciesProviding:
    
    # MARK: - Image deployer
    @property
    def card_back_image_path(self) -> str:
        return ""
    
    # MARK: - Draft List
    # Required
    @property
    def locally_managed_sets_client(self) -> DataSourceLocallyManagedSetsClientProtocol:
        raise Exception
    
    def data_source_card_search_client_provider(self,
                                                local_managed_sets_data_source: DataSourceLocallyManagedSets) -> DataSourceCardSearchClientProviding:
        raise Exception
    
    # Optional
    def draft_list_item_cell(self, 
                             trading_card: TradingCard,
                             pack_index: int, 
                             card_index: int, 
                             stylesheet: DraftListStyleSheet) -> Optional[QWidget]:
        return None
    
    def draft_list_item_header(self,
                               stylesheet: DraftListStyleSheet, 
                               text: str) -> Optional[QWidget]:
        return None
    
    def export_draft_list(self, draft_packs: List[DraftPack], to_path: str, swu_db: bool) -> None:
        return None
    
    def export_draft_list_csv(self, draft_packs: List[DraftPack], to_path: str) -> None:
        return None
    
    def draft_resource_list(self, 
                            unaggregated_list: List[LocalCardResource], 
                            aggregate_list: bool) -> Optional[List[LocalCardResource]]:
        return None
    
    def provide_draft_list_image_preview_widget(self, draft_list_data_source: DataSourceDraftList) -> QWidget:
        raise Exception