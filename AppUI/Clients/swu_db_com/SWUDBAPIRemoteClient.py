from AppCore.Data.APIClientProtocol import (APIClientProtocol,
                                            APIClientSearchCallback,
                                            NetworkerProtocol)
from AppCore.Models import SearchConfiguration

from ..SWUCardSearchConfiguration import SWUCardSearchConfiguration
from .SearchRequest import SearchRequest


# https://stackoverflow.com/a/33453124
# suggests using move to thread
class SWUDBAPIRemoteClient(APIClientProtocol):

    def __init__(self, networker: NetworkerProtocol):
        self._networker = networker

    @property
    def source_display_name(self) -> str:
        return "https://www.swu-db.com/"

    @property
    def site_source_url(self) -> str:
        return "https://www.swu-db.com/"

    def search(self, search_configuration: SearchConfiguration, callback: APIClientSearchCallback):
        swu_search_config = SWUCardSearchConfiguration.from_search_configuration(search_configuration)
        self._networker.load(SearchRequest(swu_search_config), callback)