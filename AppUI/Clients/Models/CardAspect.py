from enum import Enum
from typing import Dict, Optional

from AppUI.Clients.Assets import AssetProvider


class CardAspect(str, Enum):
    VIGILANCE = 'vigilance'
    COMMAND = 'command'
    AGGRESSION = 'aggression'
    CUNNING = 'cunning'
    HEROISM = 'heroism'
    VILLAINY = 'villainy'
    
    @property
    def rank(self) -> int:
        return self._rank_mapping()[self]
    
    @staticmethod
    def _rank_mapping() -> Dict['CardAspect', int]:
        return {
            CardAspect.VIGILANCE: 1,
            CardAspect.COMMAND: 2,
            CardAspect.AGGRESSION: 3,
            CardAspect.CUNNING: 4,
            CardAspect.HEROISM: 5,
            CardAspect.VILLAINY: 6
        }
    
    @staticmethod
    def _emoji_mapping() -> Dict['CardAspect', str]:
        return {
            CardAspect.VIGILANCE: "🔵",
            CardAspect.COMMAND: "🟢",
            CardAspect.AGGRESSION: "🔴",
            CardAspect.CUNNING: "🟡",
            CardAspect.HEROISM: "⚪",
            CardAspect.VILLAINY: "⚫"
        }
    
    @property
    def emoji(self) -> str:
        return self._emoji_mapping()[self]
    
    def aspect_image_path(self, asset_provider: AssetProvider, small: bool) -> Optional[str]:
        return asset_provider.image.aspect_resource(self.value, small)
        
        if self == CardAspect.VIGILANCE:
            return asset_provider.image.aspect_vigilance
        if self == CardAspect.COMMAND:
            return asset_provider.image.aspect_command
        if self == CardAspect.AGGRESSION:
            return asset_provider.image.aspect_aggression
        if self == CardAspect.CUNNING:
            return asset_provider.image.aspect_cunning
        if self == CardAspect.HEROISM:
            return asset_provider.image.aspect_heroism
        if self == CardAspect.VILLAINY:
            return asset_provider.image.aspect_villainy
        return None