import copy
from typing import Dict, List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QFontDatabase, QPalette, QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from AppCore.Config import ConfigurationManager
from AppCore.DataFetcher import *
from AppCore.DataSource import (DataSourceCardSearchClientProviding,
                                DataSourceLocallyManagedSets)
from AppCore.DataSource.DataSourceLocallyManagedSets import \
    DataSourceLocallyManagedSetsClientProtocol
from AppCore.Models import DraftPack, LocalCardResource, TradingCard
from AppCore.Observation import ObservationTower
from AppUI.Assets import AssetProvider
from AppUI.ExternalAppDependenciesProviding import \
    ExternalAppDependenciesProviding
from AppUI.Models import DraftListStyleSheet
from .UIComponents.DraftListItemHeader import DraftListItemHeader

from .Assets import AssetProvider as InternalAssetProvider
from AppCore.DataSource import DataSourceDraftList
from .ClientProvider import ClientProvider
from .Exporter.DraftListExporter import DraftListExporter
from .swu_db_com import SWUDBLocalSetRetrieverClient
from .Models.SWUTradingCard import SWUTradingCard
from .Models.SWUTradingCardModelMapper import SWUTradingCardModelMapper


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
        horizontal_layout = QHBoxLayout()
        cell_widget = QWidget()
        cell_widget.setLayout(horizontal_layout)
        horizontal_layout.setSpacing(stylesheet.cell_content_spacing) # needs its own
        horizontal_layout.setContentsMargins(stylesheet.cell_padding_left, 
                                            stylesheet.cell_padding_top, 
                                            stylesheet.cell_padding_right, 
                                            stylesheet.cell_padding_bottom)
        
        palette = cell_widget.palette()
        cell_style = stylesheet.get_modulo_interval_cell_style(card_index)
        if cell_style is not None:
            palette.setColor(QPalette.ColorRole.Background, QColor(cell_style.cell_background_color))
        
        cell_widget.setLayout(horizontal_layout)
        cell_widget.setAutoFillBackground(True)
        cell_widget.setPalette(palette)
        
        palette = QPalette()
        if cell_style is not None:
            palette.setColor(QPalette.ColorRole.Foreground, QColor(cell_style.cell_font_color))
            
            
        label = QLabel()
        label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        label.setPalette(palette)
        label.setText(trading_card.name)
        
        cost_label = QLabel()
        cost_label.setText(trading_card.cost)
        cost_label.setPalette(palette)
        
        custom_font_path = stylesheet.cell_font_path
        if custom_font_path is not None:
            font_id = QFontDatabase.addApplicationFont(custom_font_path)
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            custom_font = QFont(font_families[0], stylesheet.cell_font_size)
            label.setFont(custom_font)
            cost_label.setFont(custom_font)
        else:
            current_font = label.font()
            current_font.setPointSize(stylesheet.cell_font_size)
            label.setFont(current_font)
            cost_label.setFont(current_font)
        
        horizontal_layout.addWidget(label, 1)
        
        SIZE = stylesheet.cell_aspect_image_size
        
        image_view = QLabel()
        pixmap = QPixmap(1, SIZE)
        # Fill the pixmap with a transparent color (alpha value of 0)
        pixmap.fill(QColor(0, 0, 0, 0)) # R, G, B, Alpha
        image_view.setPixmap(pixmap)
        horizontal_layout.addWidget(image_view)
        
        horizontal_layout.addWidget(cost_label)
        
        swu_trading_card = SWUTradingCardModelMapper.from_trading_card(trading_card)
        if swu_trading_card is None:
            return cell_widget
        
        for a in swu_trading_card.aspects:
            image_path = a.aspect_image_path(self._internal_asset_provider, SIZE <= 50)
            if image_path is not None:
                image = QPixmap()
                image_view = QLabel()
                image.load(image_path)
                scaled_image = image.scaled(SIZE, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                image_view.setPixmap(scaled_image)
                horizontal_layout.addWidget(image_view)
                
        return cell_widget
                    
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
        return QWidget()