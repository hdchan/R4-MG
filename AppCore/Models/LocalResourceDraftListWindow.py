
import copy
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from AppCore.Models import LocalAssetResource

from .DraftPack import DraftPack

class DraftListWindowConfiguration:
    def __init__(self, 
                 window_name: str,
                 window_identifier: UUID,
                 window_height: int,
                 window_width: int,
                 draft_pack_identifier: Optional[str] = None):
        super().__init__()
        self.window_height = window_height
        self.window_width = window_width
        self.window_name = window_name
        self._window_identifier = window_identifier
        self._draft_pack_identifier = draft_pack_identifier
    
    def __eq__(self, other):  # type: ignore
        if not isinstance(other, DraftListWindowConfiguration):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self._window_identifier == other._window_identifier
    
    @property
    def window_identifier(self) -> str:
        return str(self._window_identifier)
    
    @property
    def draft_pack_identifier(self) -> Optional[str]:
        return self._draft_pack_identifier
    
    @draft_pack_identifier.setter
    def draft_pack_identifier(self, value: Optional[str]):
        self._draft_pack_identifier = value
    
    class Keys:
            WINDOW_HEIGHT = 'window_height'
            WINDOW_WIDTH = 'window_width'
            DRAFT_PACK_IDENTIFIER = 'draft_pack_identifier'
            WINDOW_IDENTIFIER = 'window_identifier'
            WINDOW_NAME = 'window_name'
    
    def to_data(self) -> Dict[str, Any]:
        return {
            self.Keys.WINDOW_HEIGHT: self.window_height,
            self.Keys.WINDOW_WIDTH: self.window_width,
            self.Keys.DRAFT_PACK_IDENTIFIER: self._draft_pack_identifier,
            self.Keys.WINDOW_IDENTIFIER: str(self.window_identifier),
            self.Keys.WINDOW_NAME: self.window_name
        }
    
    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        default = DraftListWindowConfiguration.default_window()
        return cls(
            window_name=json[cls.Keys.WINDOW_NAME],
            window_identifier=UUID(json[cls.Keys.WINDOW_IDENTIFIER]),
            window_height=json.get(cls.Keys.WINDOW_HEIGHT, default.window_height),
            window_width=json.get(cls.Keys.WINDOW_WIDTH, default.window_width),
            draft_pack_identifier=json.get(cls.Keys.DRAFT_PACK_IDENTIFIER, None),
        )
    
    @classmethod
    def default_window(cls, window_name: str = ""):
        if not window_name:
            window_name = "New Window"
        return cls(
            window_name=window_name,
            window_identifier=uuid4(),
            window_height=500,
            window_width=300
        )

class LocalResourceDraftListWindow(LocalAssetResource):
    def __init__(self,
                 window_name: str,
                 window_configuration: DraftListWindowConfiguration,
                 asset_dir: str, 
                 draft_pack: Optional[DraftPack]):
        super().__init__(asset_dir=asset_dir, 
                         file_name=window_name, 
                         file_extension='json', 
                         display_name=window_name)
        self._window_configuration = window_configuration
        self.draft_pack = draft_pack

    @property
    def window_configuration(self) -> DraftListWindowConfiguration:
        return copy.deepcopy(self._window_configuration)
    
    @window_configuration.setter
    def window_configuration(self, value: DraftListWindowConfiguration):
        self._window_configuration = value