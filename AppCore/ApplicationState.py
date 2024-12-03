from typing import Optional

from .Models import LocalCardResource


class ApplicationState:
    @property
    def current_card_search_resource(self) -> Optional[LocalCardResource]:
        return NotImplemented
    
    @property
    def can_publish_staged_resources(self) -> bool:
        return NotImplemented