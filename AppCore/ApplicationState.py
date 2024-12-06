from typing import Optional

from .Models import LocalCardResource


class ApplicationState:
    
    @property
    def can_publish_staged_resources(self) -> bool:
        return NotImplemented