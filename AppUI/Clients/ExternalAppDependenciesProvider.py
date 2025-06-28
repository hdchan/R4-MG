

import copy
import csv
import json
from typing import Dict, List, Optional

from PIL import Image
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

from .Assets import AssetProvider as InternalAssetProvider
from .CardAspect import CardAspect
from .CardType import CardType
from .ClientProvider import ClientProvider
from .swu_db_com import SWUDBLocalSetRetrieverClient
from .SWUTradingCard import SWUTradingCard
from .SWUTradingCardModelMapper import SWUTradingCardModelMapper

from PyQtUI import VerticalBoxLayout
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
        horizontal_layout = QHBoxLayout()
        cell_widget = QWidget()
        cell_widget.setLayout(horizontal_layout)
        
        horizontal_layout.setSpacing(stylesheet.cell_header_spacing) # needs its own
        horizontal_layout.setContentsMargins(stylesheet.cell_header_padding_left, 
                                            stylesheet.cell_header_padding_top, 
                                            stylesheet.cell_header_padding_right, 
                                            stylesheet.cell_header_padding_bottom)
        
        palette = cell_widget.palette()
        
        palette.setColor(QPalette.ColorRole.Background, QColor(stylesheet.cell_header_background_color))
        
        cell_widget.setLayout(horizontal_layout)
        cell_widget.setAutoFillBackground(True)
        cell_widget.setPalette(palette)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Foreground, QColor(stylesheet.cell_header_font_color))
            
            
        label = QLabel()
        label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        label.setPalette(palette)
        label.setText(text)
        
        custom_font_path = stylesheet.cell_header_font_path
        if custom_font_path is not None:
            font_id = QFontDatabase.addApplicationFont(custom_font_path)
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            custom_font = QFont(font_families[0], stylesheet.cell_header_font_size)
            label.setFont(custom_font)
        else:
            current_font = label.font()
            current_font.setPointSize(stylesheet.cell_header_font_size)
            label.setFont(current_font)
        
        horizontal_layout.addWidget(label, 1)
        
        container_widget = QWidget()
        VerticalBoxLayout([
            cell_widget
        ]).set_content_margins(0, 0, 0, 0).set_to_layout(container_widget)
        container_widget.setContentsMargins(0, 0, 0, stylesheet.cell_header_spacing)
        return container_widget
    
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
            image_path = a.aspect_image_path(self._asset_provider)
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
        # takes only first leader and base
        flat_list = [item for pack in draft_packs for item in pack.draft_list]
        
        non_empty_trading_cards: List[SWUTradingCard] = []
        no_trading_card_resources: List[LocalCardResource] = []
        
        leaders: List[SWUTradingCard] = []
        bases: List[SWUTradingCard] = []
        main_deck: List[SWUTradingCard] = []
        
        for r in flat_list:
            t = r.trading_card
            if t is None:
                no_trading_card_resources.append(r)
                continue
            swu_t = SWUTradingCardModelMapper.from_trading_card(t)
            if swu_t is None:
                continue
            non_empty_trading_cards.append(swu_t)
            
            if swu_t.type == CardType.LEADER:
                leaders.append(swu_t)
            elif swu_t.type == CardType.BASE:
                bases.append(swu_t)
            else:
                main_deck.append(swu_t)
        
        if len(leaders) == 0:
            return
        if len(bases) == 0:
            return
        
        
        def export_to_mgg():
            deck_counter: Dict[str, int] = {}
            for m in main_deck:
                hash_array: List[str] = [m.name]
                if m.subtitle is not None:
                    hash_array.append(m.subtitle)
                hash = " | ".join(hash_array)
                
                if hash not in deck_counter:
                    deck_counter[hash] = 0
                deck_counter[hash] += 1
            
            deck_result: List[str] = ["MainDeck\n"]
            for m in deck_counter.keys():
                deck_result.append(f'{deck_counter[m]} | {m}\n')
            
            result: List[str] = [
                "Leader\n",
                f"1 | {leaders[0].name} | {leaders[0].subtitle}\n",
                "Base\n",
                f"1 | {bases[0].name}\n", # no subtitle
            ] + deck_result
            
            with open(f'{to_path}your_file_melee.txt', 'w') as f:
                for r in result:
                    f.write(r)
        
        
        
        def export_to_swudb():
            deck_counter: Dict[str, int] = {}
            for m in main_deck:
                hash = f'{m.set}_{m.number}'
                if m not in deck_counter:
                    deck_counter[hash] = 0
                    
                deck_counter[hash] += 1
            
            deck_result: List[Dict[str, Any]] = []
            for m in deck_counter.keys():
                deck_result.append({
                    "id": m,
                    "count": deck_counter[m]
                })
            
            result: Dict[str, Any] = {
                "leader": {
                    "id": f'{leaders[0].set}_{leaders[0].number}',
                    "count": 1
                },
                "base": {
                    "id": f'{bases[0].set}_{bases[0].number}',
                    "count": 1
                },
                "deck": deck_result
            }
            
            with open(f'{to_path}your_file.json', 'w') as f:
                f.write(json.dumps(result))
        
        if swu_db:
            export_to_swudb()
        else:
            export_to_mgg()
            
    def export_draft_list_csv(self, draft_packs: List[DraftPack], to_path: str):
        # flat_list = [item for pack in draft_packs for item in pack.draft_list]
        aspects = [member.value for member in CardAspect]
        data: List[List[str]] = [
            [
                "original_order",
                "draft_pack",
                "set",
                "identifier",
                "name", 
                "subtitle",
                "type",
                "cost",
                "power",
                "hp"
                ] + aspects
            ]
        counter = 0
        for p in draft_packs:
            for r in p.draft_list:
                t = r.trading_card
                if t is not None:
                    swu_t = SWUTradingCardModelMapper.from_trading_card(t)
                    if swu_t is None:
                        continue
                    card_aspects = swu_t.aspects
                    counter += 1
                    more_data: List[str] = [
                        counter,
                        p.pack_name,
                        swu_t.set,
                        swu_t.set+swu_t.number,
                        swu_t.name, 
                        swu_t.subtitle,
                        swu_t.card_type,
                        swu_t.cost,
                        swu_t.power,
                        swu_t.hp,
                        ] + [member.value in card_aspects for member in CardAspect]
                    data.append(more_data)
        
        with open(f'{to_path}your_file_csv.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(data)