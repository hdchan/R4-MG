from typing import Any, Dict


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

    class Keys:
        CARD_NAME = 'card_name'
        METADATA = 'metadata'

    def to_data(self) -> Dict[str, Any]:
        return {
            self.Keys.CARD_NAME: self.card_name,
            self.Keys.METADATA: self.metadata
        }
    
    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        obj = cls.__new__(cls)
        super(SearchConfiguration, obj).__init__()
        obj.card_name = json[SearchConfiguration.Keys.CARD_NAME]
        obj.metadata = json[SearchConfiguration.Keys.METADATA]
        return obj