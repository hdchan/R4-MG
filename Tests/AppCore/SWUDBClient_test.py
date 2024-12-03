from AppCore.Models import SearchConfiguration

from ..Helpers import RandomTestCase
from ..Mocks import LocalNetworkerProtocol
from AppCore.Clients.SWUDB import SWUDBAPIRemoteClient, SearchRequest

class SWUDBAPIRemoteClient_test(RandomTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.mock_networker = LocalNetworkerProtocol()
        self.sut = SWUDBAPIRemoteClient(self.mock_networker)
        
    def tearDown(self) -> None:
        super().tearDown()
        self.mock_networker = None
        self.sut = None
        
    def test_stuff(self):
        search_config = SearchConfiguration()
        card_name = self.randomAlphaNumericString()
        def callback():
            pass
        callable = callback
        self.sut.search(search_config, callable)
        
        self.assertEqual(len(self.mock_networker.load_invocations), 1)
        expected_search_request = SearchRequest(card_name, search_config)
        self.assertEqual(self.mock_networker.load_invocations[0]['request'], expected_search_request)