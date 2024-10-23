from typing import Optional
from ..Config import ConfigurationProvider
from ..Image import ImageResourceCacher
from ..Models.LocalCardResource import LocalCardResource
from ..Models.TradingCard import TradingCard
from .CardImageSourceProtocol import CardImageSourceProtocol, CardImageSourceProviderProtocol

PNG_EXTENSION = '.png'

class CardResourceProvider:
    def __init__(self, 
                 trading_card: TradingCard,
                 configuration_provider: ConfigurationProvider,
                 card_image_source_provider: CardImageSourceProviderProtocol, 
                 resource_cacher: ImageResourceCacher):
        self._trading_card = trading_card
        self._configuration_provider = configuration_provider
        self.card_image_source_provider = card_image_source_provider
        self._resource_cacher = resource_cacher
        self._show_front: bool = True
    
    @property
    def is_flippable(self) -> bool:
        return self._trading_card.is_flippable
    
    @property
    def _card_image_source(self) -> CardImageSourceProtocol:
        return self.card_image_source_provider.provideSource()
    
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
    def _site_source_path(self) -> str:
        return self._card_image_source.site_source_identifier()
    
    @property
    def _image_path(self) -> str:
        return f'{self._configuration_provider.configuration.cache_file_path}{self._site_source_path}/'
    
    @property
    def _image_preview_path(self) -> str:
        return f'{self._configuration_provider.configuration.cache_preview_file_path}{self._site_source_path}/'
    
    @property
    def front_local_resource(self) -> LocalCardResource:
        return LocalCardResource(self._image_path, 
                                self._image_preview_path, 
                                self._unique_identifier_front,
                                self._trading_card.friendly_display_name,
                                PNG_EXTENSION, 
                                self._card_image_source.front_art_url(self._trading_card))
    
    @property
    def back_local_resource(self) -> Optional[LocalCardResource]:
        back_art_url = self._card_image_source.back_art_url(self._trading_card)
        if back_art_url is None:
            return None
        return LocalCardResource(self._image_path, 
                                self._image_preview_path, 
                                self._unique_identifier_back,
                                self._trading_card.friendly_display_name + ' (back)',
                                PNG_EXTENSION, 
                                back_art_url)
    
    @property
    def _unique_identifier_front(self) -> str:
        return self._trading_card.set + self._trading_card.number
    
    @property
    def _unique_identifier_back(self) -> str:
        return self._trading_card.set + self._trading_card.number + '-back'