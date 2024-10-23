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
        self.assertFalse(sut.is_performance_mode)
        pictures_location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation)
        self.assertEqual(sut.production_file_path, f'{pictures_location}/{sut.app_path_name}/production/')
        self.assertEqual(sut.production_preview_file_path, f'{sut.production_file_path}preview/')
        self.assertEqual(sut.cache_file_path, f'{pictures_location}/{sut.app_path_name}/cache/')
        self.assertEqual(sut.cache_preview_file_path, f'{sut.cache_file_path}preview/')
        self.assertFalse(sut.is_developer_mode)
        self.assertFalse(sut.is_mock_data)
        self.assertFalse(sut.is_delay_network_mode)
        self.assertEqual(sut.network_delay_duration, 0)
        
    def test_set_performance_mode(self):
        sut = Configuration()
        sut.is_performance_mode = True
        self.assertTrue(sut.is_performance_mode)