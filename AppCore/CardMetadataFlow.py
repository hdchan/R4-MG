
from .CardSearchFlow import CardSearchFlow
from .Image import ImageResourceDeployer
from typing import Dict, List
from .Models import CardType, SearchConfiguration
import copy
class CardMetadataFlow:
    
    def __init__(self, card_search_flow: CardSearchFlow, 
                 image_resource_deployer: ImageResourceDeployer):
        self._card_search_flow = card_search_flow
        self._image_resource_deployer = image_resource_deployer
        self._card_type_map: Dict[str, CardType] = {}
        
    @property
    def card_type_list(self) -> List[CardType]:
        return list(CardType)
    
    def set_search_configuration(self, card_type: CardType):
        search_configuration = copy.deepcopy(self._card_search_flow.search_configuration)
        search_configuration.card_type = card_type
        self._card_search_flow.user_update_search_configuration(search_configuration)
    
    def set_card_type_for_deployment_row(self, row_index: int, card_type: CardType):
        file_name = self._image_resource_deployer.production_resources[row_index].file_name
        self._card_type_map[file_name] = card_type
        
    # def toggle_
        # search_configuration = copy.deepcopy(self._card_search_flow.search_configuration)
        # search_configuration.card_type = card_type
        # self._card_search_flow.system_update_search_configuration(search_configuration)
        
        
    