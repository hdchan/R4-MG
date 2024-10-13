from typing import Optional
from .LocalCardResource import LocalCardResource

class TradingCard:
    def __init__(self, 
                 name: str, 
                 set: str, 
                 type: str, 
                 front_art: str, 
                 number: str, 
                 back_art: Optional[str] = None):
        super().__init__()
        self.name: str = name
        self.set: str = set
        self.type: str = type
        self.number: str = number
        
        self.front_art: str = front_art
        self.back_art: Optional[str] = back_art
        self.show_front: bool = True
        
        self.front_art_resource: LocalCardResource
        self.back_art_resource: Optional[LocalCardResource]

    @property
    def is_flippable(self) -> bool:
        return self.back_art is not None

    def flip(self):
        self.show_front = not self.show_front

    @property
    def unique_identifier(self) -> str:
        if self.show_front:
            return self.set + self.number
        else:
            return self.set + self.number + '-back'


    @property
    def image_url(self) -> str:
        if self.show_front:
            return self.front_art
        else:
            if self.back_art is None:
                return self.front_art
            else:
                return self.back_art
            
    @property
    def local_resource(self) -> LocalCardResource:
        if self.show_front:
            return self.front_art_resource
        else:
            if self.back_art_resource is None:
                return self.front_art_resource
            else:
                return self.back_art_resource
            
    
    @property
    def friendly_display_name(self) -> str:
        if self.show_front:
            return f'[{self.set+self.number}] {self.name} - {self.type}'
        else:
            return f'[{self.set+self.number}] {self.name} - {self.type} (back)'
    
    @property
    def unique_identifier_front(self) -> str:
        return self.set + self.number
    
    @property
    def unique_identifier_back(self) -> str:
        return self.set + self.number + '-back'
    
    @property
    def friendly_display_name_front(self) -> str:
        return f'[{self.set+self.number}] {self.name} - {self.type}'
    
    @property
    def friendly_display_name_back(self) -> str:
        return f'[{self.set+self.number}] {self.name} - {self.type} (back)'
    
