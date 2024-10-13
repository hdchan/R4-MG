from .Requests import SearchRequest
from ...Data.APIClientProtocol import (APIClientProtocol,
                                       APIClientSearchCallback)

# https://stackoverflow.com/a/33453124
# suggests using move to thread
class SWUDBClient(APIClientProtocol):

    def search(self, query: str, callback: APIClientSearchCallback):
        self.netorker.load(SearchRequest(query), callback)
        
      