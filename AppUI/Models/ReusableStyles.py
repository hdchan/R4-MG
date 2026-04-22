from typing import Dict, Any, Optional


class EdgeDimensions:
    class Defaults:
        def __init__(self, left: int = 0, top: int = 0, right: int = 0, bottom: int = 0):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    def __init__(self,
                 prefix: str,
                 json: Dict[str, Any],
                 defaults: Optional['EdgeDimensions'.Defaults] = None):
        self._prefix = prefix
        self._json = json
        self._defaults = self.Defaults()

    @property
    def left(self) -> int:
        return self._json.get(f'{self._prefix}_left', self._defaults.left)

    @property
    def top(self) -> int:
        return self._json.get(f'{self._prefix}_top', self._defaults.top)

    @property
    def right(self) -> int:
        return self._json.get(f'{self._prefix}_right', self._defaults.right)

    @property
    def bottom(self) -> int:
        return self._json.get(f'{self._prefix}_bottom', self._defaults.bottom)


class PaddingDimension(EdgeDimensions):
    def __init__(self,
                 prefix: str,
                 json: Dict[str, Any],
                 defaults: Optional['EdgeDimensions'.Defaults] = None):
        super().__init__(f'{prefix}_padding', json, defaults)
