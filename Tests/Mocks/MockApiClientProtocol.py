from AppCore.Data.APIClientProtocol import (APIClientProtocol,
                                            APIClientSearchCallback)
from AppCore.Models import SearchConfiguration
from AppCore.Network import NetworkerProtocol


class MockAPIClientProtocol(APIClientProtocol):
    
    def __init__(self, networker: NetworkerProtocol):
        super().__init__(networker)
        self.search_invocations = []
    
    
    def search(self, search_configuration: SearchConfiguration, callback: APIClientSearchCallback):
        self.search_invocations.append({"card_name": search_configuration.card_name, 
                                        "search_configuration": search_configuration, 
                                        "callback": callback})