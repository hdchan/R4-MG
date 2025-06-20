from PyQt5.QtCore import QStandardPaths

from AppCore.Config import Configuration

from ..Helpers import RandomTestCase


class Configuration_test(RandomTestCase):
    def setUp(self) -> None:
        super().setUp()
    
    def tearDown(self) -> None:
        super().tearDown()
        
    def test_init(self):
        sut = Configuration()
        self.assertEqual(sut.app_display_name, 'R4-MG')
        self.assertEqual(sut.app_path_name, 'R4-MG')
        self.assertFalse(sut.hide_image_preview)
        pictures_location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation)
        self.assertEqual(sut.production_dir_path, f'{pictures_location}/{sut.app_path_name}/production/')
        self.assertEqual(sut.production_preview_dir_path, f'{sut.production_dir_path}preview/')
        self.assertEqual(sut.cache_card_search_dir_path, f'{pictures_location}/{sut.app_path_name}/cache/')
        self.assertEqual(sut.cache_card_search_preview_dir_path, f'{sut.cache_card_search_dir_path}preview/')
        self.assertFalse(sut.is_developer_mode)
        self.assertFalse(sut.is_mock_data)
        self.assertFalse(sut.is_delay_network_mode)
        self.assertEqual(sut.network_delay_duration, 0)
        
    def test_set_hide_image_preview(self):
        sut = Configuration()
        sut.hide_image_preview = True
        self.assertTrue(sut.hide_image_preview)