import copy
from typing import Dict, List, Optional

from PyQt5.QtWidgets import QTextEdit, QWidget, QAction

from AppCore.Config import ConfigurationManager
from AppCore.DataFetcher import *
from AppCore.DataSource import (DataSourceCardSearchClientProviding,
                                DataSourceImageResourceDeployer,
                                DataSourceLocallyManagedSets)
from AppCore.DataSource.DataSourceLocallyManagedSets import \
    DataSourceLocallyManagedSetsClientProtocol
from AppCore.Models import LocalCardResource
from AppCore.Observation import ObservationTower
from AppUI.ExternalAppDependenciesProviding import (
    ExternalAppDependenciesProviding, SearchQueryBarViewProviding)
from AppUI.Models import DraftListStyleSheet
from AppUI.Router.Router import Router
from R4UI import RMenuListBuilder, RWidget, VerticalBoxLayout

from .Assets import AssetProvider as InternalAssetProvider
from .ClientProvider import ClientProvider
from .Config.SWUAppConfiguration import SWUAppConfigurationManager
from .ExporterImporter.DraftListExporter import DraftListExporter
from .ExporterImporter.ImporterFlow import ImporterFlow
from .Models.SWUTradingCard import SWUTradingCard
from .Models.SWUTradingCardModelMapper import SWUTradingCardModelMapper
from .swu_db_com import SWUDBLocalSetRetrieverClient
from .SWUAppDependenciesProviding import SWUAppDependenciesProviding
from .UIComponents.AboutViewController import AboutViewController
from .UIComponents.AddImageCTAViewController import AddImageCTAViewController
from .UIComponents.DraftListImagePreviewViewController import \
    DraftListImagePreviewViewController
from .UIComponents.DraftListItemCell import DraftListItemCell
from .UIComponents.DraftListItemHeader import DraftListItemHeader
from .UIComponents.SearchQueryBarViewController import \
    SearchQueryBarViewController


class SWUAppDelegate(ExternalAppDependenciesProviding):
    
    def __init__(self, 
                 swu_app_dependencies_provider: SWUAppDependenciesProviding,
                 configuration_manager: ConfigurationManager):
        self._swu_app_dependencies_provider = swu_app_dependencies_provider
        self._configuration_manager = configuration_manager
        self._locally_managed_sets_client = SWUDBLocalSetRetrieverClient()
        self._draft_list_exporter = DraftListExporter()
        self._data_source_card_search_client_provider: Optional[DataSourceCardSearchClientProviding] = None
    
    @property
    def _swu_app_configuration_manager(self) -> SWUAppConfigurationManager:
        return self._swu_app_dependencies_provider.configuration_manager

    @property
    def _observation_tower(self) -> ObservationTower:
        return self._swu_app_dependencies_provider.observation_tower
    
    @property
    def _internal_asset_provider(self) -> InternalAssetProvider:
        return self._swu_app_dependencies_provider.asset_provider

    # MARK: - Card search
    def provide_card_search_query_view(self) -> Optional[SearchQueryBarViewProviding]:
        return SearchQueryBarViewController()

    # MARK: - Image deployer
    @property
    def card_back_image_path(self) -> str:
        return self._internal_asset_provider.image.swu_card_back
    
    @property
    def logo_path(self) -> str:
        return self._internal_asset_provider.image.logo_path
    
    @property
    def image_preview_logo_path(self) -> str:
        return self._internal_asset_provider.image.swu_logo_black_path
    
    def hook_developer_menu(self, menu: RMenuListBuilder) -> Optional[RMenuListBuilder]:
        return menu

    def provide_about_view_controller(self) -> RWidget:
        return AboutViewController(self._configuration_manager, self._internal_asset_provider)

    def provide_additional_quick_guide(self) -> Optional[RWidget]:
        with open(self._internal_asset_provider.text.shortcuts_path, 'r', encoding='utf-8') as file:
            data = file.read()
        markdown = QTextEdit()
        markdown.setMarkdown(data)
        markdown.setReadOnly(True)
        return VerticalBoxLayout([
            markdown
        ])

    # MARK: - Draft List

    def provide_image_deployer_banner_cta(self, 
                                          data_source_image_resource_deployer: DataSourceImageResourceDeployer, 
                                          router: Router) -> Optional[RWidget]:
        return AddImageCTAViewController(self._observation_tower, data_source_image_resource_deployer, self._internal_asset_provider, router)

    def data_source_card_search_client_provider(self,
                                                local_managed_sets_data_source: DataSourceLocallyManagedSets) -> DataSourceCardSearchClientProviding:
        if self._data_source_card_search_client_provider is not None:
            return self._data_source_card_search_client_provider
        
        client_provider = ClientProvider(self._swu_app_dependencies_provider, 
                                         local_managed_sets_data_source)
        self._data_source_card_search_client_provider = client_provider
        return client_provider
    
    @property
    def locally_managed_sets_client(self) -> DataSourceLocallyManagedSetsClientProtocol:
        return self._locally_managed_sets_client
    
    def draft_list_item_header(self,
                               stylesheet: DraftListStyleSheet, 
                               text: str) -> Optional[QWidget]:
        return DraftListItemHeader(stylesheet, text)
    
    def draft_list_item_cell(self, 
                             local_card_resource: LocalCardResource,
                             pack_index: int, 
                             card_index: int, 
                             stylesheet: DraftListStyleSheet, 
                             is_presentation: bool) -> Optional[QWidget]:
        resource = SWUTradingCardModelMapper.from_card_resource(local_card_resource)
        if resource is None:
            return None
        return DraftListItemCell(stylesheet, 
                                 card_index, 
                                 resource,
                                 self._internal_asset_provider, 
                                 is_presentation)
                    
    # TODO: aggregate by type?
    def draft_resource_list(self, unaggregated_list: List[LocalCardResource], aggregate_list: bool) -> Optional[List[LocalCardResource]]:
        if not aggregate_list:
            return unaggregated_list
        counters: Dict[SWUTradingCard, int] = {}
        for resource in unaggregated_list:
            trading_card = resource.trading_card
            if trading_card is None: 
                continue
            swu_trading_card = SWUTradingCard.from_json(trading_card.to_data())
            
            if swu_trading_card not in counters:
                counters[swu_trading_card] = 0
            counters[swu_trading_card] += 1
        counter_copy = copy.deepcopy(counters)
        
        result: List[LocalCardResource] = []
        
        for resource in unaggregated_list:
            trading_card = resource.trading_card
            if trading_card is None: 
                continue
            swu_trading_card = SWUTradingCard.from_json(trading_card.to_data())
            counter_copy[swu_trading_card] -= 1
            
            if counter_copy[swu_trading_card] == 0:
                if counters[swu_trading_card] > 1:
                    swu_trading_card.name = f'{counters[swu_trading_card]}x {swu_trading_card.name}'
                resource.trading_card = swu_trading_card
                result.append(resource)
        return result
    
    def export_draft_list(self):
        self._swu_app_dependencies_provider
        self._draft_list_exporter.export_draft_list(self._swu_app_dependencies_provider)

    def import_draft_list(self):
        importer = ImporterFlow(self._swu_app_dependencies_provider)
        importer.start()
        
    def provide_draft_list_image_preview_widget(self) -> QWidget:
        return DraftListImagePreviewViewController(self._swu_app_dependencies_provider)