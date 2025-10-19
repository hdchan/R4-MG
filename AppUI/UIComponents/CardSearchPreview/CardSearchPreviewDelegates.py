from AppCore.Models import (DataSourceSelectedLocalCardResourceProtocol,
                                LocalResourceDataSourceProviding)
from AppCore.ImageResource.ImageResourceProcessorProtocol import *
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding

from .CardSearchPreviewViewController import (
    CardSearchPreviewViewController, CardSearchPreviewViewControllerDelegate)
from .CustomDirectorySearchTableViewController import (
    CustomDirectorySearchTableViewController,
    CustomDirectorySearchTableViewControllerDelegate)
from .CacheHistoryTableViewController import (
    CacheHistoryTableViewController,
    CacheHistoryTableViewControllerDelegate)
from .SearchTableViewController import (
    SearchTableViewController, SearchTableViewControllerDelegate)

class CardSearchPreviewDelegates:

    class ImageDeploymentCardSearchPreviewDelegate( 
                                                         CardSearchPreviewViewControllerDelegate, 
                                                         LocalResourceDataSourceProviding, 
                                                         SearchTableViewControllerDelegate, 
                                                         CustomDirectorySearchTableViewControllerDelegate, 
                                                         CacheHistoryTableViewControllerDelegate):
        class TabKeys:
            CUSTOM_DIR_SEARCH = 0
            CARD_SEARCH = 1
            PUBLISH_HISTORY = 2

        def __init__(self, app_dependencies_provider: AppDependenciesInternalProviding):
            

            self._recent_published_data_source = app_dependencies_provider.data_source_recent_published

            self._custom_dir_search_table_view = CustomDirectorySearchTableViewController(app_dependencies_provider)
            self._custom_dir_search_table_view.delegate = self
            
            configuration = SearchTableViewController.SearchTableViewControllerConfiguration('search_history', 40)
            self._search_table_view = SearchTableViewController(app_dependencies_provider,
                                                                configuration)
            self._search_table_view.delegate = self
            
            
            
            self._publish_history_list = CacheHistoryTableViewController(app_dependencies_provider, 
                                                                        self._recent_published_data_source)
            self._publish_history_list.delegate = self
            
            self._vcs: List[LocalResourceDataSourceProviding] = [
                self._custom_dir_search_table_view,
                self._search_table_view,
                self._publish_history_list
            ]

            self._titles = [
                "Custom Dir",
                "Card Search",
                "Publish History"
            ]

            self._card_search_preview = CardSearchPreviewViewController(app_dependencies_provider, self)

            

        @property
        def data_source(self) -> DataSourceSelectedLocalCardResourceProtocol:
            return self._card_search_preview

        @property
        def csp_tab_count(self) -> int:
            return len(self._vcs)
        
        def csp_local_resource_providing_vc(self, index: int) -> LocalResourceDataSourceProviding:
            return self._vcs[index]
        
        def csp_tab_name(self, index: int) -> str:
            return self._titles[index]
        
        def stvc_did_retrieve_card(self) -> None:
            self._card_search_preview.set_retrieved_resource_from_vc(self.TabKeys.CARD_SEARCH)

        def cds_did_retrieve_card(self) -> None:
            self._card_search_preview.set_retrieved_resource_from_vc(self.TabKeys.CUSTOM_DIR_SEARCH)

        def ch_did_retrieve_card(self) -> None:
            self._card_search_preview.set_retrieved_resource_from_vc(self.TabKeys.PUBLISH_HISTORY)


    class DraftListCardSearchPreviewDelegate(
                                                   CardSearchPreviewViewControllerDelegate,
                                                   LocalResourceDataSourceProviding, 
                                                   SearchTableViewControllerDelegate):
        class TabKeys:
            CARD_SEARCH = 0

        def __init__(self, app_dependencies_provider: AppDependenciesInternalProviding):
            
            
            configuration = SearchTableViewController.SearchTableViewControllerConfiguration()
            self._search_table_view = SearchTableViewController(app_dependencies_provider,
                                                                configuration)
            self._search_table_view.delegate = self
            
            
            self._vcs: List[LocalResourceDataSourceProviding] = [
                self._search_table_view,
            ]

            self._titles = [
                "Card Search",
            ]

            self._card_search_preview = CardSearchPreviewViewController(app_dependencies_provider, self)

        @property
        def data_source(self) -> DataSourceSelectedLocalCardResourceProtocol:
            return self._card_search_preview

        @property
        def csp_tab_count(self) -> int:
            return len(self._vcs)
        
        def csp_local_resource_providing_vc(self, index: int) -> LocalResourceDataSourceProviding:
            return self._vcs[index]
        
        def csp_tab_name(self, index: int) -> str:
            return self._titles[index]
        
        def stvc_did_retrieve_card(self) -> None:
            self._card_search_preview.set_retrieved_resource_from_vc(self.TabKeys.CARD_SEARCH)