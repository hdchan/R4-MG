from AppCore.Models import TradingCard

from ..Helpers import RandomTestCase


class TradingCard_test(RandomTestCase):
    def setUp(self) -> None:
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()
    
    def test_init(self):
        expected_name = self.randomAlphaNumericString()
        expected_set = self.randomAlphaNumericString()
        expected_type = self.randomAlphaNumericString()
        expected_front_art = self.randomAlphaNumericString()
        expected_number = self.randomAlphaNumericString()
        expected_back_art = self.randomOptional(self.randomAlphaNumericString())
        sut = TradingCard(name=expected_name, 
                          set=expected_set, 
                          type=expected_type, 
                          front_art=expected_front_art, 
                          number=expected_number, 
                          back_art=expected_back_art)
        
        self.assertEqual(sut.name, expected_name)
        self.assertEqual(sut.set, expected_set)
        self.assertEqual(sut.type, expected_type)
        self.assertEqual(sut.front_art, expected_front_art)
        self.assertEqual(sut.number, expected_number)
        self.assertEqual(sut.back_art, expected_back_art)
        
    def test_given_no_back_art_is_flippable_returns_false(self):
        sut = self.randomTradingCard(back_art=None)
        self.assertEqual(sut.is_flippable, False)
        
    def test_given_has_back_art_is_flippable_returns_true(self):
        sut = self.randomTradingCard(back_art=self.randomAlphaNumericString())
        self.assertEqual(sut.is_flippable, True)
    
    def test_flip(self):
        sut = self.randomTradingCard()
        self.assertTrue(sut.show_front)
        
        sut.flip()
        self.assertFalse(sut.show_front)
    
    def test_unique_identifier_name(self):
        expected_set = self.randomAlphaNumericString()
        expected_number = self.randomAlphaNumericString()
        sut = self.randomTradingCard(set=expected_set, number=expected_number)
        self.assertEqual(sut.unique_identifier, expected_set + expected_number)
        
        sut.flip()
        self.assertEqual(sut.unique_identifier, expected_set + expected_number + '-back')
        
    def test_image_url(self):
        expected_front_art = self.randomAlphaNumericString()
        expected_back_art = self.randomAlphaNumericString()
        sut = self.randomTradingCard(front_art=expected_front_art, back_art=expected_back_art)
        self.assertEqual(sut.image_url, expected_front_art)
        
        sut.flip()
        self.assertEqual(sut.image_url, expected_back_art)
    
        
    