from typing import Any, Dict, Optional
# Should only be subclassed
class TradingCard():
    def __init__(self,
                 name: str, 
                 set: str, 
                 type: str,
                 number: str,
                 cost: Optional[str],
                 power: Optional[str],
                 hp: Optional[str],
                 json: Dict[str, Any],
                 metadata: Dict[str, Any] = {}):
        super().__init__()
        self.name: str = name
        self.set: str = set
        self.type: str = type
        self.number: str = number
        self.cost: Optional[str] = cost
        self.power: Optional[str] = power
        self.hp: Optional[str] = hp
        self.json = json
        self.metadata = metadata
    
    class Keys:
        NAME = 'name'
        SET = 'set'
        TYPE = 'type'
        NUMBER = 'number'
        COST = 'cost'
        POWER = 'power'
        HP = 'hp'
        METADATA = 'metadata'
        JSON = 'json'

    def __hash__(self):
        return hash((self.set, self.number))
    
    def __eq__(self, other):  # type: ignore
        if not isinstance(other, TradingCard):
            # don't attempt to compare against unrelated types
            raise NotImplementedError

        return self.set == other.set and \
            self.number == other.number

    def to_data(self) -> Dict[str, Any]:
        return {
            self.Keys.NAME: self.name,
            self.Keys.SET: self.set,
            self.Keys.TYPE: self.type,
            self.Keys.NUMBER: self.number,
            self.Keys.COST: self.cost,
            self.Keys.POWER: self.power,
            self.Keys.HP: self.hp,
            self.Keys.METADATA: self.metadata,
            self.Keys.JSON: self.json
        }
    
    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        obj = cls.__new__(cls)
        obj.name = json[TradingCard.Keys.NAME]
        obj.set = json[TradingCard.Keys.SET]
        obj.type = json[TradingCard.Keys.TYPE]
        obj.number = json[TradingCard.Keys.NUMBER]
        obj.cost = json.get(TradingCard.Keys.COST, None)
        obj.power = json.get(TradingCard.Keys.POWER, None)
        obj.hp = json.get(TradingCard.Keys.HP, None)
        obj.metadata = json[TradingCard.Keys.METADATA]
        obj.json = json.get(TradingCard.Keys.JSON, {})
        return obj
    
    @property
    def friendly_display_name_short(self) -> str:
        return f'{self.set+self.number}'

    @property
    def friendly_display_name(self) -> str:
        return f'[{self.set+self.number}] {self.name} - {self.type}'
    
    @property
    def friendly_display_name_detailed(self) -> str:
        return f'[{self.set+self.number}] {self.name} - {self.type}'
    
    @property
    def front_art_url(self) -> str:
        raise NotImplementedError
    
    @property
    def back_art_url(self) -> Optional[str]:
        raise NotImplementedError