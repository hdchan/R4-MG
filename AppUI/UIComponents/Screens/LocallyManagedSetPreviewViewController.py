from typing import List, Optional, Any

from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from AppCore.Config import Configuration
from AppCore.DataSource.DataSourceCardSearch import (
    DataSourceCardSearch, DataSourceCardSearchClientProtocol,
    DataSourceCardSearchClientProviding, DataSourceCardSearchClientSearchResponse,
     DataSourceCardSearchClientSearchResult,
    DataSourceCardSearchClientSearchCallback, DataSourceCardSearchDelegate)
from AppCore.Models import (LocalAssetResource, PaginationConfiguration,
                            SearchConfiguration, LocalCardResource, TradingCard)
from AppUI.AppDependenciesProviding import AppDependenciesProviding
from AppUI.UIComponents.Base import ImagePreviewViewController
from AppUI.UIComponents.Base import (
    SearchTableComboViewController, SearchTableComboViewControllerDelegate)
from AppCore.DataFetcher import DataFetcherLocal


class LocallyManagedSetPreviewViewController(QWidget, SearchTableComboViewControllerDelegate, DataSourceCardSearchDelegate, DataSourceCardSearchClientProtocol, DataSourceCardSearchClientProviding):
    
    def __init__(self,
                 app_dependencies_provider: AppDependenciesProviding,
                 resource: LocalAssetResource):
        super().__init__()
        self.setMinimumSize(800, 600)
        self._resource = resource
        self._card_search_data_source = app_dependencies_provider.new_instance_card_search_data_source(self, self)
        self._local_managed_sets_data_source = app_dependencies_provider.local_managed_sets_data_source
        self._local_fetcher = DataFetcherLocal(app_dependencies_provider.configuration_manager)

        self._selected_resource: Optional[LocalCardResource] = None
        self._card_resources = self._local_managed_sets_data_source.retrieve_set_card_list(resource)
        
        self.setWindowTitle(f'Set preview: {resource.display_name.upper()} ({len(self._card_resources)} cards)')
        
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        search_table_combo_view = SearchTableComboViewController(self)
        layout.addWidget(search_table_combo_view, 7)
        self._search_table_combo_view = search_table_combo_view
        
        
        v_layout = QVBoxLayout()
        v_layout_widget = QWidget()
        v_layout_widget.setLayout(v_layout)
        layout.addWidget(v_layout_widget, 5)
        
        
        
        image_preview = ImagePreviewViewController(app_dependencies_provider)
        v_layout.addWidget(image_preview)
        self._image_preview_view = image_preview
        
        placholder_widget = QWidget()
        v_layout.addWidget(placholder_widget, 1)

        self._vc_search() # initial loading
    
    def _vc_search(self):
        stripped_text = self._search_table_combo_view.card_name_search_bar_text.strip()
        search_configuration = SearchConfiguration()
        search_configuration.card_name = stripped_text
        
        self._card_search_data_source.search(search_configuration)

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
    
    def client(self, setting: Configuration.Settings.SearchSource) -> DataSourceCardSearchClientProtocol:
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
            self._image_preview_view.set_image(self._card_search_data_source.current_selected_card_search_resource)
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