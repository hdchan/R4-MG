from typing import Optional, Dict, Any
from ..Models import CardType

class ResourceMetadata:
    def __init__(self):
        self.card_type: Optional[CardType] = None
    
    def loadJSON(self, json: Dict[str, Any]):
        if 'card_type' in json:
            for i in CardType:
                if i.value == json.get('card_type'):
                    self.card_type = i
                    break
        
    def toJSON(self) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {
            
        }
        if self.card_type is not None:
            metadata['card_type'] = self.card_type.value
        return metadata