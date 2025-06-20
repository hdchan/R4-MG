from AppCore.DataSource.DataSourceCardSearchClientProtocol import (DataSourceCardSearchClientProtocol,
                                            DataSourceCardSearchClientSearchCallback)
from AppCore.Models import SearchConfiguration
from AppCore.DataFetcher import NetworkerProtocol


class MockDataSourceCardSearchClientProtocol(DataSourceCardSearchClientProtocol):
    
    def __init__(self, networker: NetworkerProtocol):
        super().__init__(networker)
        self.search_invocations = []
    
    
    def search(self, search_configuration: SearchConfiguration, callback: DataSourceCardSearchClientSearchCallback):
        self.search_invocations.append({"card_name": search_configuration.card_name, 
                                        "search_configuration": search_configuration, 
                                        "callback": callback})