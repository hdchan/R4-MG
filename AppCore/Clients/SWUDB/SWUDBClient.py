from .Requests import SearchRequest
from ...Data.APIClientProtocol import (APIClientProtocol,
                                       APIClientSearchCallback)
from ...Models import SearchConfiguration

# https://stackoverflow.com/a/33453124
# suggests using move to thread
class SWUDBClient(APIClientProtocol):

    def search(self, card_name: str, search_configuration: SearchConfiguration, callback: APIClientSearchCallback):
        self.netorker.load(SearchRequest(card_name, search_configuration), callback)
        
      