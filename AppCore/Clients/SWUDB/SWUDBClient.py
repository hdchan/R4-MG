from .Requests import SearchRequest
from ...Data.APIClientProtocol import (APIClientProtocol,
                                       APIClientSearchCallback)
from ...Models import SearchConfiguration

# https://stackoverflow.com/a/33453124
# suggests using move to thread
class SWUDBClient(APIClientProtocol):

    @property
    def site_source_url(self) -> str:
        return "https://www.swu-db.com/"

    def search(self, search_configuration: SearchConfiguration, callback: APIClientSearchCallback):
        self.netorker.load(SearchRequest(search_configuration), callback)
        
      