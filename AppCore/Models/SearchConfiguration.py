from typing import Dict, Any


class SearchConfiguration:
    def __init__(self):
        self.card_name: str = ""
        self.metadata: Dict[str, Any] = {}
        
    def __eq__(self, other):  # type: ignore
        if not isinstance(other, SearchConfiguration):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (self.card_name == other.card_name and 
                self.metadata == other.metadata)