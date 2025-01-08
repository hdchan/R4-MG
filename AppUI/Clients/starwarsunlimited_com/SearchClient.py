from AppCore.Data.APIClientProtocol import (APIClientProtocol,
                                            APIClientSearchCallback,
                                            NetworkerProtocol)
from AppCore.Models import SearchConfiguration

from ...Assets import AssetProvider
from ..SWUCardSearchConfiguration import SWUCardSearchConfiguration
from .SearchRequest import SearchRequest


class SearchClient(APIClientProtocol):

    def __init__(self, networker: NetworkerProtocol, asset_provider: AssetProvider):
        self._networker = networker
        self._asset_provider = asset_provider

    @property
    def source_display_name(self) -> str:
        return "https://www.starwarsunlimited.com/"

    @property
    def site_source_url(self) -> str:
        return "www.starwarsunlimited.com"

    def search(self, search_configuration: SearchConfiguration, callback: APIClientSearchCallback):
        swu_search_config = SWUCardSearchConfiguration.from_search_configuration(search_configuration)
        self._networker.load(SearchRequest(swu_search_config, self._asset_provider), callback)