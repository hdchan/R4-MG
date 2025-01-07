from typing import Optional

from ..Config import ConfigurationManager
from ..Models.LocalCardResource import LocalCardResource
from ..Models.TradingCard import TradingCard
from .CardImageSourceProtocol import (CardImageSourceProtocol,
                                      CardImageSourceProviding)

PNG_EXTENSION = '.png'

class CardResourceProvider:
    def __init__(self, 
                 trading_card: TradingCard,
                 configuration_manager: ConfigurationManager,
                 card_image_source_provider: CardImageSourceProviding):
        self._trading_card = trading_card
        self._configuration_manager = configuration_manager
        self.card_image_source_provider = card_image_source_provider
        self._show_front: bool = True
    
    @property
    def is_flippable(self) -> bool:
        return self._trading_card.is_flippable
    
    @property
    def _card_image_source(self) -> CardImageSourceProtocol:
        return self.card_image_source_provider.card_image_source
    
    def flip(self):
        if self.is_flippable:
            self._show_front = not self._show_front
    
    @property
    def local_resource(self) -> LocalCardResource:
        if self._show_front:
            return self.front_local_resource
        else:
            if self.back_local_resource is None:
                return self.front_local_resource
            else:
                return self.back_local_resource
    
    @property
    def front_local_resource(self) -> LocalCardResource:
        return LocalCardResource(image_dir=self._card_image_source.image_path,
                                 image_preview_dir=self._card_image_source.image_preview_dir, 
                                 file_name=self._unique_identifier_front,
                                 display_name=self._trading_card.friendly_display_name,
                                 display_name_short=self._trading_card.friendly_display_name_short,
                                 display_name_detailed=self._trading_card.friendly_display_name_detailed,
                                 file_extension=PNG_EXTENSION, 
                                 remote_image_url=self._card_image_source.front_art_url(self._trading_card))
    
    @property
    def back_local_resource(self) -> Optional[LocalCardResource]:
        back_art_url = self._card_image_source.back_art_url(self._trading_card)
        if back_art_url is None:
            return None
        return LocalCardResource(image_dir=self._card_image_source.image_path,
                                 image_preview_dir=self._card_image_source.image_preview_dir, 
                                 file_name=self._unique_identifier_back,
                                 display_name=self._trading_card.friendly_display_name + ' (back)',
                                 display_name_short=self._trading_card.friendly_display_name_short + ' (back)',
                                 display_name_detailed=self._trading_card.friendly_display_name_detailed + ' (back)',
                                 file_extension=PNG_EXTENSION, 
                                 remote_image_url=back_art_url)
    
    @property
    def _unique_identifier_front(self) -> str:
        return self._trading_card.set + self._trading_card.number
    
    @property
    def _unique_identifier_back(self) -> str:
        return self._trading_card.set + self._trading_card.number + '-back'