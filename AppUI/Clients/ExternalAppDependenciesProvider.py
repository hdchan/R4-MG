import copy
from typing import Dict, List, Optional

from PyQt5.QtWidgets import QWidget

from AppCore.Config import ConfigurationManager
from AppCore.DataFetcher import *
from AppCore.DataSource import (DataSourceCardSearchClientProviding,
                                DataSourceDraftList,
                                DataSourceLocallyManagedSets)
from AppCore.DataSource.DataSourceLocallyManagedSets import \
    DataSourceLocallyManagedSetsClientProtocol
from AppCore.Models import DraftPack, LocalCardResource, TradingCard
from AppCore.Observation import ObservationTower
from AppUI.Assets import AssetProvider
from AppUI.ExternalAppDependenciesProviding import \
    ExternalAppDependenciesProviding
from AppUI.Models import DraftListStyleSheet

from .Assets import AssetProvider as InternalAssetProvider
from .ClientProvider import ClientProvider
from .Exporter.DraftListExporter import DraftListExporter
from .Models.SWUTradingCard import SWUTradingCard
from .swu_db_com import SWUDBLocalSetRetrieverClient
from .UIComponents.DraftListItemCell import DraftListItemCell
from .UIComponents.DraftListItemHeader import DraftListItemHeader
from .UIComponents.DraftListImagePreviewViewController import DraftListImagePreviewViewController

class ExternalAppDependenciesProvider(ExternalAppDependenciesProviding):
    
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 configuration_manager: ConfigurationManager, 
                 asset_provider: AssetProvider):
        self._asset_provider = asset_provider
        self._internal_asset_provider = InternalAssetProvider()
        self._observation_tower = observation_tower
        self._configuration_manager = configuration_manager
        self._locally_managed_sets_client = SWUDBLocalSetRetrieverClient()
        self._draft_list_exporter = DraftListExporter()
        self._data_source_card_search_client_provider: Optional[DataSourceCardSearchClientProviding] = None 
    
    # MARK: - Image deployer
    @property
    def card_back_image_path(self) -> str:
        return self._internal_asset_provider.image.swu_card_back
    
    # MARK: - Draft List
    
    def data_source_card_search_client_provider(self,
                                                local_managed_sets_data_source: DataSourceLocallyManagedSets) -> DataSourceCardSearchClientProviding:
        if self._data_source_card_search_client_provider is not None:
            return self._data_source_card_search_client_provider
        
        client_provider_dependencies = ClientProvider.Dependencies(self._asset_provider,
                                                                   self._internal_asset_provider,
                                                                       DataFetcherRemote(self._configuration_manager),
                                                                       DataFetcherLocal(self._configuration_manager),
                                                                       local_managed_sets_data_source)
        client_provider = ClientProvider(dependencies=client_provider_dependencies)
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
                             trading_card: TradingCard, 
                             pack_index: int, 
                             card_index: int, 
                             stylesheet: DraftListStyleSheet) -> Optional[QWidget]:
        return DraftListItemCell(stylesheet, card_index, trading_card, self._internal_asset_provider)
                    
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
    
    def export_draft_list(self, draft_packs: List[DraftPack], to_path: str, swu_db: bool):
        self._draft_list_exporter.export_draft_list(draft_packs, to_path, swu_db)
        
    def provide_draft_list_image_preview_widget(self, draft_list_data_source: DataSourceDraftList) -> QWidget:
        return DraftListImagePreviewViewController(self._observation_tower, draft_list_data_source)