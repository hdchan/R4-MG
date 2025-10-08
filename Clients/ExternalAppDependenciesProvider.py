import copy
from typing import Dict, List, Optional

from PyQt5.QtWidgets import QWidget, QTextEdit

from AppCore.Config import ConfigurationManager
from AppCore.DataFetcher import *
from AppCore.DataSource import (DataSourceCardSearchClientProviding,
                                DataSourceDraftList,
                                DataSourceImageResourceDeployer,
                                DataSourceLocallyManagedSets)
from AppCore.DataSource.DataSourceLocallyManagedSets import \
    DataSourceLocallyManagedSetsClientProtocol
from AppCore.Models import DraftPack, LocalCardResource, TradingCard
from AppCore.Observation import ObservationTower
from AppUI.Assets import AssetProvider
from AppUI.ExternalAppDependenciesProviding import \
    ExternalAppDependenciesProviding
from AppUI.Models import DraftListStyleSheet
from AppUI.Router import Router
from R4UI import R4UIWidget, VerticalBoxLayout

from .Assets import AssetProvider as InternalAssetProvider
from .ClientProvider import ClientProvider
from .Exporter.DraftListExporter import DraftListExporter
from .Models.SWUTradingCard import SWUTradingCard
from .swu_db_com import SWUDBLocalSetRetrieverClient
from .UIComponents.AboutViewController import AboutViewController
from .UIComponents.AddImageCTAViewController import AddImageCTAViewController
from .UIComponents.DraftListImagePreviewViewController import \
    DraftListImagePreviewViewController
from .UIComponents.DraftListItemCell import DraftListItemCell
from .UIComponents.DraftListItemHeader import DraftListItemHeader
from .Models.SWUTradingCardModelMapper import SWUTradingCardModelMapper
from .Config.SWUAppConfiguration import SWUAppConfigurationManager
class ExternalAppDependenciesProvider(ExternalAppDependenciesProviding):
    
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 configuration_manager: ConfigurationManager, 
                 asset_provider: AssetProvider):
        self._asset_provider = asset_provider
        self._internal_asset_provider = InternalAssetProvider()
        self._observation_tower = observation_tower
        self._configuration_manager = configuration_manager
        self._swu_app_configuration_manager = SWUAppConfigurationManager(self._configuration_manager)
        self._locally_managed_sets_client = SWUDBLocalSetRetrieverClient()
        self._draft_list_exporter = DraftListExporter()
        self._data_source_card_search_client_provider: Optional[DataSourceCardSearchClientProviding] = None 
    
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
    
    def provide_about_view_controller(self) -> R4UIWidget:
        return AboutViewController(self._configuration_manager, self._internal_asset_provider)

    def provide_additional_quick_guide(self) -> Optional[R4UIWidget]:
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
                                          router: Router) -> Optional[R4UIWidget]:
        return AddImageCTAViewController(self._observation_tower, data_source_image_resource_deployer, self._internal_asset_provider, router)

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
    
    def export_draft_list(self, draft_packs: List[DraftPack], to_path: str, swu_db: bool):
        self._draft_list_exporter.export_draft_list(draft_packs, to_path, swu_db)
        
    def provide_draft_list_image_preview_widget(self, draft_list_data_source: DataSourceDraftList) -> QWidget:
        return DraftListImagePreviewViewController(self._observation_tower, 
                                                   draft_list_data_source, 
                                                   self._swu_app_configuration_manager)