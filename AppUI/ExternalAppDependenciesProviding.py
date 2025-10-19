
from typing import List, Optional

from AppCore.DataSource import (DataSourceCardSearchClientProviding,
                                DataSourceImageResourceDeployer,
                                DataSourceLocallyManagedSets)
from AppCore.DataSource.DataSourceLocallyManagedSets import \
    DataSourceLocallyManagedSetsClientProtocol
from AppCore.Models import LocalCardResource, SearchConfiguration
from AppUI.ExternalAppDependenciesProviding import *
from AppUI.Models import DraftListStyleSheet
from AppUI.Router.Router import Router
from R4UI import RWidget, R4UIMenuListBuilder
from AppCore.Models import LocalCardResource
from typing import Dict, Any

class SearchQueryBarViewProviding(RWidget):
    @property
    def search_configuration(self) -> SearchConfiguration:
        raise Exception
    
    @property
    def secondary_search_configuration(self) -> Optional[SearchConfiguration]:
        return None

    @property
    def tertiary_search_configuration(self) -> Optional[SearchConfiguration]:
        return None
    
    def did_receive_configuration(self, search_configuration: SearchConfiguration) -> None:
        return
    
    def set_search_focus(self) -> None:
        return
    
    def reset_search(self) -> None:
        return
    
    def set_enabled(self, is_on: bool) -> None:
        return

class ExternalAppDependenciesProviding:
    
    @property
    def logo_path(self) -> str:
        return ""
    
    def hook_developer_menu(self, menu: R4UIMenuListBuilder) -> Optional[R4UIMenuListBuilder]:
        return None

    # MARK: - Card search
    def provide_card_search_query_view(self) -> Optional[SearchQueryBarViewProviding]:
        return None

    # MARK: - Image deployer
    @property
    def card_back_image_path(self) -> str:
        return ""
    
    @property
    def image_preview_logo_path(self) -> str:
        return ""
    
    def provide_about_view_controller(self) -> RWidget:
        raise Exception
    
    def provide_additional_quick_guide(self) -> Optional[RWidget]:
        return None
    
    # MARK: - Draft List
    def provide_image_deployer_banner_cta(self, 
                                          data_source_image_resource_deployer: DataSourceImageResourceDeployer, 
                                          router: Router) -> Optional[RWidget]:
        return None

    @property
    def locally_managed_sets_client(self) -> DataSourceLocallyManagedSetsClientProtocol:
        raise Exception
    
    def data_source_card_search_client_provider(self,
                                                local_managed_sets_data_source: DataSourceLocallyManagedSets) -> DataSourceCardSearchClientProviding:
        raise Exception
    
    def provide_draft_list_image_preview_widget(self) -> RWidget:
        raise Exception
    
    # Optional
    def draft_list_item_cell(self, 
                             local_card_resource: LocalCardResource,
                             pack_index: int, 
                             card_index: int, 
                             stylesheet: DraftListStyleSheet, 
                             is_presentation: bool) -> Optional[RWidget]:
        return None
    
    def draft_list_item_header(self,
                               stylesheet: DraftListStyleSheet, 
                               text: str) -> Optional[RWidget]:
        return None
    
    def export_draft_list(self) -> None:
        return None
    
    def import_draft_list(self) -> None:
        return None
    
    def draft_resource_list(self, 
                            unaggregated_list: List[LocalCardResource], 
                            aggregate_list: bool) -> Optional[List[LocalCardResource]]:
        return None
    
    