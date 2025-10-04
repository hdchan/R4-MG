
from typing import List, Optional

from PyQt5.QtWidgets import QWidget

from AppCore.DataSource import (DataSourceCardSearchClientProviding,
                                DataSourceDraftList,
                                DataSourceImageResourceDeployer,
                                DataSourceLocallyManagedSets)
from AppCore.DataSource.DataSourceLocallyManagedSets import \
    DataSourceLocallyManagedSetsClientProtocol
from AppCore.Models import DraftPack, LocalCardResource, TradingCard
from AppUI.ExternalAppDependenciesProviding import *
from AppUI.Models import DraftListStyleSheet
from R4UI import R4UIWidget
from AppUI.Router import Router

class ExternalAppDependenciesProviding:
    
    # MARK: - Image deployer
    @property
    def card_back_image_path(self) -> str:
        return ""
    
    @property
    def logo_path(self) -> str:
        return ""
    
    @property
    def image_preview_logo_path(self) -> str:
        return ""
    
    def provide_about_view_controller(self) -> R4UIWidget:
        raise Exception
    
    def provide_additional_quick_guide(self) -> Optional[R4UIWidget]:
        return None
    
    # MARK: - Draft List
    def provide_image_deployer_banner_cta(self, 
                                          data_source_image_resource_deployer: DataSourceImageResourceDeployer, 
                                          router: Router) -> Optional[R4UIWidget]:
        return None

    @property
    def locally_managed_sets_client(self) -> DataSourceLocallyManagedSetsClientProtocol:
        raise Exception
    
    def data_source_card_search_client_provider(self,
                                                local_managed_sets_data_source: DataSourceLocallyManagedSets) -> DataSourceCardSearchClientProviding:
        raise Exception
    
    # Optional
    def draft_list_item_cell(self, 
                             local_card_resource: LocalCardResource,
                             pack_index: int, 
                             card_index: int, 
                             stylesheet: DraftListStyleSheet, 
                             is_presentation: bool) -> Optional[QWidget]:
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