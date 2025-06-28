
import copy
from typing import Any, Dict, Optional

from AppCore.Models import LocalAssetResource

from .DraftPack import DraftPack

YAML_EXTENSION = 'yaml'

class DraftListWindowConfiguration:
    def __init__(self, 
                 window_height: int, 
                 window_width: int,
                 draft_pack_name: Optional[str] = None):
        super().__init__()
        self.window_height = window_height
        self.window_width = window_width
        self.draft_pack_name = draft_pack_name
    
    def __eq__(self, other):  # type: ignore
        if not isinstance(other, DraftListWindowConfiguration):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.window_height == other.window_height and \
            self.window_width == other.window_width and \
                self.draft_pack_name == other.draft_pack_name
    
    class Keys:
            WINDOW_HEIGHT = 'window_height'
            WINDOW_WIDTH = 'window_width'
            DRAFT_PACK_NAME = 'draft_pack_name'
    
    def to_data(self) -> Dict[str, Any]:
        return {
            self.Keys.WINDOW_HEIGHT: self.window_height,
            self.Keys.WINDOW_WIDTH: self.window_width,
            self.Keys.DRAFT_PACK_NAME: self.draft_pack_name
        }
    
    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        default = DraftListWindowConfiguration.default_window()
        return cls(
            window_height=json.get(cls.Keys.WINDOW_HEIGHT, default.window_height),
            window_width=json.get(cls.Keys.WINDOW_WIDTH, default.window_width),
            draft_pack_name=json.get(cls.Keys.DRAFT_PACK_NAME, None)
        )
    
    @classmethod
    def default_window(cls):
        return cls(
            window_height=500,
            window_width=300,
        )

class LocalResourceDraftListWindow(LocalAssetResource):
    def __init__(self,
                 window_name: str,
                 window_configuration: DraftListWindowConfiguration,
                 asset_dir: str, 
                 draft_pack: Optional[DraftPack]):
        super().__init__(asset_dir=asset_dir, 
                         file_name=window_name, 
                         file_extension=YAML_EXTENSION, 
                         display_name=window_name)
        self._window_configuration = window_configuration
        self.draft_pack = draft_pack

    @property
    def window_configuration(self) -> DraftListWindowConfiguration:
        return copy.deepcopy(self._window_configuration)
    
    @window_configuration.setter
    def window_configuration(self, value: DraftListWindowConfiguration):
        self._window_configuration = value