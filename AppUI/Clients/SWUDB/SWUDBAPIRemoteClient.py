from AppCore.Data.APIClientProtocol import (APIClientProtocol,
                                            APIClientSearchCallback)
from AppCore.Models import SearchConfiguration

from .Requests import SearchRequest, SWUDBAPISearchConfiguration


# https://stackoverflow.com/a/33453124
# suggests using move to thread
class SWUDBAPIRemoteClient(APIClientProtocol):

    @property
    def site_source_url(self) -> str:
        return "https://www.swu-db.com/"

    def search(self, search_configuration: SearchConfiguration, callback: APIClientSearchCallback):
        swu_search_config = SWUDBAPISearchConfiguration.from_search_configuration(search_configuration)
        self.netorker.load(SearchRequest(swu_search_config), callback)
        
      