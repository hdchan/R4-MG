from typing import Dict, Any, Optional, Tuple

class WindowDimensions:
    WINDOW_WIDTH_PREFIX = 'window_width_'
    WINDOW_HEIGHT_PREFIX = 'window_height_'
    
    def __init__(self, values: Dict[str, int]):
        self._values = values
        
    def to_data(self) -> Dict[str, Any]:
        return self._values
    
    @classmethod
    def default(cls):
        return cls({})
    
    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        return cls(json)
    
    def window_dimensions(self, identifier: str) -> Optional[Tuple[int, int]]:
        width = self.window_width(identifier)
        height = self.window_height(identifier)
        if width is None or height is None:
            return None
        return (width, height)
    
    def window_width(self, identifier: str) -> Optional[int]:
        key = f'{WindowDimensions.WINDOW_WIDTH_PREFIX}{identifier}'
        if key in self._values:
            return self._values[key]
        return None
    
    def set_window_width(self, identifier: str, value: int):
        key = f'{WindowDimensions.WINDOW_WIDTH_PREFIX}{identifier}'
        self._values[key] = value
    
    def window_height(self, identifier: str) -> Optional[int]:
        key = f'{WindowDimensions.WINDOW_HEIGHT_PREFIX}{identifier}'
        if key in self._values:
            return self._values[key]
        return None
    
    def set_window_height(self, identifier: str, value: int):
        key = f'{WindowDimensions.WINDOW_HEIGHT_PREFIX}{identifier}'
        self._values[key] = value
        
    def set_window_dimensions(self, identifier: str, width: int, height: int):
        self.set_window_height(identifier, height)
        self.set_window_width(identifier, width)