from AppCore.Models import SearchConfiguration

from ..Helpers import RandomTestCase
from ..Mocks import NetworkerLocalProtocol
from AppCore.Clients.SWUDB import SWUDBAPIRemoteClient, SearchRequest

class SWUDBAPIRemoteClient_test(RandomTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.local_networker = NetworkerLocalProtocol()
        self.sut = SWUDBAPIRemoteClient(self.local_networker)
        
    def tearDown(self) -> None:
        super().tearDown()
        self.local_networker = None
        self.sut = None
        
    def test_stuff(self):
        search_config = SearchConfiguration()
        card_name = self.randomAlphaNumericString()
        def callback():
            pass
        callable = callback
        self.sut.search(search_config, callable)
        
        self.assertEqual(len(self.local_networker.load_invocations), 1)
        expected_search_request = SearchRequest(card_name, search_config)
        self.assertEqual(self.local_networker.load_invocations[0]['request'], expected_search_request)