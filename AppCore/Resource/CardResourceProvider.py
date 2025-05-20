import re
from typing import Optional
from urllib.parse import urlparse

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
    def trading_card(self) -> TradingCard:
        return self._trading_card
    
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
        # TODO: rework
        if self._trading_card.local_image_path is not None:
            return LocalCardResource(image_dir=self._trading_card.local_image_path,
                                    image_preview_dir=self._trading_card.local_image_path, # need to regenerate preview image?
                                    file_name=self._trading_card.name,
                                    display_name=self._trading_card.friendly_display_name,
                                    display_name_short=self._trading_card.friendly_display_name_short,
                                    display_name_detailed=self._trading_card.friendly_display_name_detailed,
                                    file_extension=PNG_EXTENSION, 
                                    remote_image_url=None)
        else:
            return LocalCardResource(image_dir=self._image_path,
                                    image_preview_dir=self._image_preview_dir, 
                                    file_name=self._file_name_front,
                                    display_name=self._trading_card.friendly_display_name,
                                    display_name_short=self._trading_card.friendly_display_name_short,
                                    display_name_detailed=self._trading_card.friendly_display_name_detailed,
                                    file_extension=PNG_EXTENSION, 
                                    remote_image_url=self._trading_card.front_art_url)
    
    @property
    def back_local_resource(self) -> Optional[LocalCardResource]:
        back_art_url = self._trading_card.back_art_url
        if back_art_url is None or self._file_name_back is None:
            return None
        return LocalCardResource(image_dir=self._image_path,
                                 image_preview_dir=self._image_preview_dir, 
                                 file_name=self._file_name_back,
                                 display_name=self._trading_card.friendly_display_name + ' (back)',
                                 display_name_short=self._trading_card.friendly_display_name_short + ' (back)',
                                 display_name_detailed=self._trading_card.friendly_display_name_detailed + ' (back)',
                                 file_extension=PNG_EXTENSION, 
                                 remote_image_url=back_art_url)
    
    @property
    def _file_name_front(self) -> str:
        return self.replace_non_alphanumeric(self._trading_card.front_art_url, "_")
    
    @property
    def _file_name_back(self) -> Optional[str]:
        if self._trading_card.back_art_url is not None:
            return self.replace_non_alphanumeric(self._trading_card.back_art_url, "_")
        return None
    
    @property
    def _image_path(self) -> str:
        domain = urlparse(self._trading_card.front_art_url).netloc
        return f'{self._configuration_manager.configuration.cache_dir_path}{domain}/'
    
    @property
    def _image_preview_dir(self) -> str:
        domain = urlparse(self._trading_card.front_art_url).netloc
        return f'{self._configuration_manager.configuration.cache_preview_dir_path}{domain}/'
    
    def replace_non_alphanumeric(self, text: str, replacement: str = '') -> str:
        """Replaces non-alphanumeric characters in a string with a specified replacement.

        Args:
            text: The input string.
            replacement: The string to replace non-alphanumeric characters with.
            Defaults to an empty string.

        Returns:
            The modified string with non-alphanumeric characters replaced.
        """
        return re.sub(r'[^a-zA-Z0-9]', replacement, text)