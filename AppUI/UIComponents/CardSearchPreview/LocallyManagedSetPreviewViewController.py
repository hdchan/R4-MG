from typing import Any, List, Optional

from AppCore.DataFetcher import DataFetcherLocal
from AppCore.Models import (DataSourceSelectedLocalCardResourceProtocol,
                                LocalResourceDataSourceProviding)
from AppCore.DataSource.DataSourceCardSearch import (
    DataSourceCardSearch, DataSourceCardSearchClientProtocol,
    DataSourceCardSearchClientProviding,
    DataSourceCardSearchClientSearchCallback,
    DataSourceCardSearchClientSearchResponse,
    DataSourceCardSearchClientSearchResult, DataSourceCardSearchDelegate)
from AppCore.Models import (LocalAssetResource, LocalCardResource,
                            PaginationConfiguration, SearchConfiguration,
                            TradingCard)
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from R4UI import RWidget, HorizontalBoxLayout

from .SearchTableComboViewController import (
    SearchTableComboViewController, SearchTableComboViewControllerDelegate)


class LocallyManagedSetPreviewViewControllerDelegate:
    def lmsp_did_retrieve_card(self) -> None:
        return

class LocallyManagedSetPreviewViewController(RWidget, 
                                             SearchTableComboViewControllerDelegate, 
                                             DataSourceCardSearchDelegate, 
                                             DataSourceCardSearchClientProtocol, 
                                             DataSourceCardSearchClientProviding,
                                             LocalResourceDataSourceProviding, 
                                             DataSourceSelectedLocalCardResourceProtocol):
    
    def __init__(self,
                 app_dependencies_provider: AppDependenciesInternalProviding,
                 resource: LocalAssetResource):
        super().__init__()
        self._resource = resource
        self._card_search_data_source = app_dependencies_provider.new_instance_card_search_data_source(self, self)
        self._local_managed_sets_data_source = app_dependencies_provider.local_managed_sets_data_source
        self._local_fetcher = DataFetcherLocal(DataFetcherLocal.Configuration(app_dependencies_provider.configuration_manager.configuration.network_delay_duration))
        self.delegate: Optional[LocallyManagedSetPreviewViewControllerDelegate] = None

        self._selected_resource: Optional[LocalCardResource] = None
        self._card_resources = self._local_managed_sets_data_source.retrieve_set_card_list(resource)
        
        self.setWindowTitle(f'Set preview: {resource.display_name.upper()} ({len(self._card_resources)} cards)') # TODO: why does this not show?

        self._search_table_combo_view = SearchTableComboViewController(app_dependencies_provider, self)

        HorizontalBoxLayout([
            self._search_table_combo_view
        ]).set_layout_to_widget(self)

        self._vc_search() # initial loading
    
    def _vc_search(self):

        self._card_search_data_source.search(self._search_table_combo_view.search_configuration)

    # MARK: - DataSourceCardSearchClientProtocol 
    @property
    def source_display_name(self) -> str:
        return self._resource.display_name.upper()
        
    def search(self,
                search_configuration: SearchConfiguration,
                pagination_configuration: PaginationConfiguration,
                callback: DataSourceCardSearchClientSearchCallback) -> None:
        def completed_search(result: DataSourceCardSearchClientSearchResult):
            callback(result)
        self._local_fetcher.load(self._perform_search, completed_search, search_configuration=search_configuration)

    def _perform_search(self, args: Any) -> DataSourceCardSearchClientSearchResult:
        search_configuration: SearchConfiguration = args.get('search_configuration')
        def filter_the_result(card: TradingCard):
            return (search_configuration.card_name.lower() in card.name.lower())
        def sort_the_result(card: TradingCard):
            return card.name
        filtered_list = list(filter(filter_the_result, self._card_resources))
        filtered_list.sort(key=sort_the_result)
        result = DataSourceCardSearchClientSearchResponse(filtered_list)
        return (result, None)
    

    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        return self._card_search_data_source.current_selected_card_search_resource

    @property
    def data_source(self) -> DataSourceSelectedLocalCardResourceProtocol:
        return self

    @property
    def search_client(self) -> DataSourceCardSearchClientProtocol:
        return self
    
    # MARK: - DataSourceCardSearchDelegate
    def ds_completed_search_with_result(self,
                                        ds: DataSourceCardSearch,
                                        search_configuration: SearchConfiguration,
                                        error: Optional[Exception], 
                                        is_initial_load: bool) -> None:
        self._search_table_combo_view.load_list()
        self._search_table_combo_view.sync_ui()

    def ds_did_retrieve_card_resource_for_card_selection(self, 
                                                        ds: DataSourceCardSearch) -> None:
        if self._card_search_data_source.current_selected_card_search_resource is not None:
            if self.delegate is not None:
                self.delegate.lmsp_did_retrieve_card()
            self._search_table_combo_view.sync_ui()
    
    # MARK: - SearchTableComboViewControllerDelegate
    def stc_select_card_resource_for_card_selection(self, stc: SearchTableComboViewController, index: int) -> None:
        self._card_search_data_source.select_card_resource_for_card_selection(index)
    
    def stc_did_click_search(self, stc: SearchTableComboViewController) -> None:
        self._vc_search()
        
    @property
    def stc_list_items(self) -> List[str]:
        return self._card_search_data_source.trading_card_display_names
    
    def stc_tapped_flip_button(self, stc: SearchTableComboViewController) -> None:
        self._card_search_data_source.flip_current_previewed_card()
    
    @property
    def stc_is_flippable(self) -> bool:
        return self._card_search_data_source.current_previewed_trading_card_is_flippable
    
    @property
    def is_only_text_search(self) -> bool:
        return True