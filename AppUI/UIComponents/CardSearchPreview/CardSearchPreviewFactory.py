from AppCore.Config import Configuration
from AppCore.ImageResource.ImageResourceProcessorProtocol import *
from AppCore.Models import (DataSourceSelectedLocalCardResourceProtocol,
                            LocalAssetResource,
                            LocalResourceDataSourceProviding)
from AppCore.Observation import (TransmissionProtocol,
                                 TransmissionReceiverProtocol)
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        SocketRouterUpdatedEvent)
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from R4UI import Label, PushButton, RWidget, VerticalBoxLayout

from .CacheHistoryTableViewController import (
    CacheHistoryTableViewController, CacheHistoryTableViewControllerDelegate)
from .CardSearchPreviewViewController import (
    CardSearchPreviewViewController, CardSearchPreviewViewControllerDelegate)
from .CustomDirectorySearchTableViewController import (
    CustomDirectorySearchTableViewController,
    CustomDirectorySearchTableViewControllerDelegate)
from .LocallyManagedSetPreviewViewController import (
    LocallyManagedSetPreviewViewController,
    LocallyManagedSetPreviewViewControllerDelegate)
from .SearchTableViewController import (SearchTableViewController,
                                        SearchTableViewControllerDelegate)


class CardSearchPreviewFactory:

    class ImageDeploymentCardSearchPreviewViewController(RWidget, 
                                                         CardSearchPreviewViewControllerDelegate, 
                                                         LocalResourceDataSourceProviding, 
                                                         SearchTableViewControllerDelegate, 
                                                         CustomDirectorySearchTableViewControllerDelegate, 
                                                         CacheHistoryTableViewControllerDelegate):

        def __init__(self, app_dependencies_provider: AppDependenciesInternalProviding):
            super().__init__()

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

            VerticalBoxLayout([
                self._card_search_preview
            ]).set_layout_to_widget(self).set_uniform_content_margins(0)

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
            self._card_search_preview.set_retrieved_resource_from_vc(self._vcs.index(self._search_table_view))

        def cds_did_retrieve_card(self) -> None:
            self._card_search_preview.set_retrieved_resource_from_vc(self._vcs.index(self._custom_dir_search_table_view))

        def ch_did_retrieve_card(self) -> None:
            self._card_search_preview.set_retrieved_resource_from_vc(self._vcs.index(self._publish_history_list))


    class DraftListCardSearchPreviewViewController(RWidget,
                                                   CardSearchPreviewViewControllerDelegate,
                                                   LocalResourceDataSourceProviding, 
                                                   SearchTableViewControllerDelegate, 
                                                   LocallyManagedSetPreviewViewControllerDelegate):
        
        class StatusWidget(RWidget, TransmissionReceiverProtocol):
            def __init__(self, app_dependencies_provider: AppDependenciesInternalProviding):
                super().__init__()
                self._configuration_manager = app_dependencies_provider.configuration_manager
                self._observation_tower = app_dependencies_provider.observation_tower
                self._socket_router = app_dependencies_provider.socket_router

                self._observation_tower.subscribe_multi(self, [ConfigurationUpdatedEvent, 
                                                               SocketRouterUpdatedEvent])

                self._setup_view()

            def _setup_view(self):
                self._status_label = Label()
                self._connect_button = PushButton(None, self._connect)
                VerticalBoxLayout([
                    self._status_label,
                    self._connect_button
                ]).set_layout_to_widget(self).set_uniform_content_margins(0)

                self._sync_ui()

            @property
            def _configuration(self) -> Configuration:
                return self._configuration_manager.configuration

            def _connect(self):
                if self._socket_router.is_connected_to_socket:
                    self._socket_router.disconnect()
                else:
                    self._socket_router.connect_if_possible()

            def _sync_ui(self):
                url = "No connection saved"
                saved_url = self._configuration.remote_socket_url
                if saved_url is not None:
                    status = "🔴 Not connected"
                    self._connect_button.set_text("Connect")
                    self._connect_button.setEnabled(True)
                    if self._socket_router.is_connected_to_socket:
                        status = "🟢 Connected"
                        self._connect_button.set_text("Disconnect")
                        self._connect_button.setEnabled(True)
                    elif self._socket_router.is_establishing_connection:
                        status = "🟡 Connecting..."
                        self._connect_button.set_text("Connecting...")
                        self._connect_button.setEnabled(False)

                    url = f'Status: {status} to {saved_url}'
                    
                self._status_label.set_text(url)

            def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
                if type(event) == ConfigurationUpdatedEvent or \
                    type(event) == SocketRouterUpdatedEvent :
                    self._sync_ui()


        def __init__(self, app_dependencies_provider: AppDependenciesInternalProviding):
            super().__init__()
            self._configuration_manager = app_dependencies_provider.configuration_manager
            

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

            if self._configuration_manager.configuration.is_remote_socket_connection_enabled:
                self._socket_io_history_list = app_dependencies_provider.data_source_socket_io

                self._socket_io_history_list = CacheHistoryTableViewController(app_dependencies_provider, 
                                                                            self._socket_io_history_list)
                self._socket_io_history_list.delegate = self
                self._socket_io_history_list.append_widget(self.StatusWidget(app_dependencies_provider))

                self._vcs.insert(0, self._socket_io_history_list)
                self._titles.insert(0, "Satellite")

            self._card_search_preview = CardSearchPreviewViewController(app_dependencies_provider, self)

            VerticalBoxLayout([
                self._card_search_preview
            ]).set_layout_to_widget(self).set_uniform_content_margins(0)

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
            self._card_search_preview.set_retrieved_resource_from_vc(self._vcs.index(self._search_table_view))

        def ch_did_retrieve_card(self) -> None:
            self._card_search_preview.set_retrieved_resource_from_vc(self._vcs.index(self._socket_io_history_list))

    class LocallyManagedSetPreviewViewController(RWidget,
                                                 CardSearchPreviewViewControllerDelegate,
                                                 LocalResourceDataSourceProviding, 
                                                 SearchTableViewControllerDelegate):

        def __init__(self, 
                     app_dependencies_provider: AppDependenciesInternalProviding, 
                     local_asset_resource: LocalAssetResource):
            super().__init__()
            
            self._search_table_view = LocallyManagedSetPreviewViewController(app_dependencies_provider,
                                                                             local_asset_resource)
            self._search_table_view.delegate = self

            self._card_search_preview = CardSearchPreviewViewController(app_dependencies_provider, self)

            VerticalBoxLayout([
                self._card_search_preview
            ]).set_layout_to_widget(self).set_uniform_content_margins(0)

        @property
        def data_source(self) -> DataSourceSelectedLocalCardResourceProtocol:
            return self._card_search_preview
        
        def csp_local_resource_providing_vc(self, index: int) -> LocalResourceDataSourceProviding:
            return self._search_table_view
        
        def lmsp_did_retrieve_card(self) -> None:
            self._card_search_preview.set_retrieved_resource_from_vc()

        @property
        def csp_is_vertical_orientation(self) -> bool:
            return False