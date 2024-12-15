import webbrowser
from typing import Callable

from PyQt5.QtWidgets import QAction, QMenu, QMenuBar

from AppCore.Config.ConfigurationManager import *
from AppCore.Service import PlatformServiceProtocol, PlatformServiceProvider

class MenuActionCoordinator(QMenuBar):
    def __init__(self, 
                 configuration_manager: ConfigurationManager, 
                 platform_service_provider: PlatformServiceProvider):
        super().__init__()
        self._configuration_manager = configuration_manager
        self._platform_service_provider = platform_service_provider
        self.build_menu_bar()
        
        
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration

    @property
    def _platform_service(self) -> PlatformServiceProtocol:
        return self._platform_service_provider.platform_service

    def build_menu_bar(self):
        # MARK: - File
        self._file_menu = QMenu("&File")
        self.addMenu(self._file_menu)

        self._new_file_menu = QAction('New image file')
        self._new_file_menu.triggered.connect(self.did_toggle_card_title_detail_detailed)
        self._file_menu.addAction(self._new_file_menu)

        self._refresh_production_images = QAction('Refresh production images')
        self._file_menu.addAction(self._refresh_production_images)
        
        self._open_production_dir = QAction('Reveal images in file explorer')
        self._open_production_dir.triggered.connect(self.did_open_production_dir)
        self._file_menu.addAction(self._open_production_dir)
        
        # Actions
        self._action_menu = QMenu("&Action")
        self.addMenu(self._action_menu)

        self._unstage_all_staging_resources = QAction('Unstage all staging resources')
        self._action_menu.addAction(self._unstage_all_staging_resources)

        self._clear_cache_dir = QAction('Clear cache')
        self._action_menu.addAction(self._clear_cache_dir)

        
        # MARK: - Settings
        self._settings_menu = QAction("Settings")
        self._file_menu.addAction(self._settings_menu)
        
        # MARK: - View
        self._view_menu = QMenu("&View")
        self.addMenu(self._view_menu)
        
        self._show_resource_details = QAction('Show resource details')
        self._show_resource_details.triggered.connect(self.did_toggle_show_resource_details)
        self._show_resource_details.setCheckable(True)
        self._show_resource_details.setChecked(self._configuration.show_resource_details)
        self._view_menu.addAction(self._show_resource_details)
        
        
        self._hide_image_preview = QAction('Hide image preview')
        self._hide_image_preview.triggered.connect(self.did_toggle_hide_image_preview)
        self._hide_image_preview.setCheckable(True)
        self._hide_image_preview.setChecked(self._configuration.hide_image_preview)
        self._view_menu.addAction(self._hide_image_preview)


        self._hide_deployment_cell_controls = QAction('Hide deployment cell controls')
        self._hide_deployment_cell_controls.triggered.connect(self.did_toggle_hide_deployment_cell_controls)
        self._hide_deployment_cell_controls.setCheckable(True)
        self._hide_deployment_cell_controls.setChecked(self._configuration.hide_deployment_cell_controls)
        self._view_menu.addAction(self._hide_deployment_cell_controls)


        self._card_title_detail = QMenu('Card title detail')
        self._view_menu.addMenu(self._card_title_detail)

        self._card_title_detail_short = QAction('Short')
        self._card_title_detail_short.triggered.connect(self.did_toggle_card_title_detail_short)
        self._card_title_detail_short.setCheckable(True)
        self._card_title_detail.addAction(self._card_title_detail_short)

        self._card_title_detail_normal = QAction('Normal')
        self._card_title_detail_normal.triggered.connect(self.did_toggle_card_title_detail_normal)
        self._card_title_detail_normal.setCheckable(True)
        self._card_title_detail.addAction(self._card_title_detail_normal)

        self._card_title_detail_detailed = QAction('Detailed')
        self._card_title_detail_detailed.triggered.connect(self.did_toggle_card_title_detail_detailed)
        self._card_title_detail_detailed.setCheckable(True)
        self._card_title_detail.addAction(self._card_title_detail_detailed)

        self._sync_card_title_detail_checkmarks()

        self._reset_window_size = QAction('Reset window size')
        self._reset_window_size.triggered.connect(self.did_toggle_reset_window_size)
        self._view_menu.addAction(self._reset_window_size)

        
        # MARK: - About
        self._help_menu = QMenu("&Help")
        self.addMenu(self._help_menu)

        self._check_update = QAction('Check for updates')
        self._check_update.triggered.connect(self.open_update_page)
        self._help_menu.addAction(self._check_update)

        self._about_action = QAction("About")
        self._help_menu.addAction(self._about_action)

        # MARK: - Developer
        if self._configuration.is_developer_mode:
            self._developer_menu = QMenu("&Developer")
            self.addMenu(self._developer_menu)

            self._open_configuration_dir = QAction('Reveal configuration in file explorer')
            self._open_configuration_dir.triggered.connect(self.did_open_configuration_dir)
            self._developer_menu.addAction(self._open_configuration_dir)

            self._open_temp_dir = QAction('Reveal temp folder in file explorer')
            self._open_temp_dir.triggered.connect(self.did_open_temp_dir)
            self._developer_menu.addAction(self._open_temp_dir)

            self._mock_data_mode = QAction('Mock data')
            self._mock_data_mode.triggered.connect(self.did_toggle_mock_data_mode)
            self._mock_data_mode.setCheckable(True)
            self._mock_data_mode.setChecked(self._configuration.is_mock_data)
            self._developer_menu.addAction(self._mock_data_mode)
            
            self._delay_network_mode = QAction('Delay network call')
            self._delay_network_mode.triggered.connect(self.did_toggle_delay_network_mode)
            self._delay_network_mode.setCheckable(True)
            self._delay_network_mode.setChecked(self._configuration.is_delay_network_mode)
            self._developer_menu.addAction(self._delay_network_mode)

    # MARK: - binders
    def bind_new_file(self, fn: Callable[[], None]):
        self._new_file_menu.triggered.connect(fn)

    def bind_refresh_production_images(self, fn: Callable[[], None]):
        self._refresh_production_images.triggered.connect(fn)

    def bind_unstage_all_staging_resources(self, fn: Callable[[], None]):
        self._unstage_all_staging_resources.triggered.connect(fn)

    def bind_clear_cache_dir(self, fn: Callable[[], None]):
        self._clear_cache_dir.triggered.connect(fn)

    def bind_open_settings_page(self, fn: Callable[[], None]):
        self._settings_menu.triggered.connect(fn)

    def bind_open_about_page(self, fn: Callable[[], None]):
        self._about_action.triggered.connect(fn)

    # MARK: - actions
    def did_toggle_show_resource_details(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_show_resource_details(is_on)
        self._configuration_manager.save_configuration(new_config)

    def did_toggle_hide_image_preview(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_hide_image_preview(is_on)
        self._configuration_manager.save_configuration(new_config)

    def did_toggle_hide_deployment_cell_controls(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_hide_deployment_cell_controls(is_on)
        self._configuration_manager.save_configuration(new_config)

    def did_toggle_mock_data_mode(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_is_mock_data(is_on)
        self._configuration_manager.save_configuration(new_config)

    def did_toggle_delay_network_mode(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_is_delay_network_mode(is_on)
        self._configuration_manager.save_configuration(new_config)
    
    def did_toggle_card_title_detail_short(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_card_title_detail(Configuration.Settings.CardTitleDetail.SHORT)
        self._configuration_manager.save_configuration(new_config)
        self._sync_card_title_detail_checkmarks()

    def did_toggle_card_title_detail_normal(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_card_title_detail(Configuration.Settings.CardTitleDetail.NORMAL)
        self._configuration_manager.save_configuration(new_config)
        self._sync_card_title_detail_checkmarks()

    def did_toggle_card_title_detail_detailed(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_card_title_detail(Configuration.Settings.CardTitleDetail.DETAILED)
        self._configuration_manager.save_configuration(new_config)
        self._sync_card_title_detail_checkmarks()

    def did_toggle_reset_window_size(self):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.reset_window_size()
        self._configuration_manager.save_configuration(new_config)

    def _sync_card_title_detail_checkmarks(self):
        preference = self._configuration.card_title_detail
        self._card_title_detail_short.setChecked(preference == Configuration.Settings.CardTitleDetail.SHORT)
        self._card_title_detail_normal.setChecked(preference == Configuration.Settings.CardTitleDetail.NORMAL)
        self._card_title_detail_detailed.setChecked(preference == Configuration.Settings.CardTitleDetail.DETAILED)
    
    def did_open_configuration_dir(self):
        self._platform_service.open_file(self._configuration.config_directory)

    def did_open_production_dir(self):
        self._platform_service.open_file(self._configuration.production_dir_path)

    def did_open_temp_dir(self):
        self._platform_service.open_file(self._configuration.temp_dir_path)
        
    def open_update_page(self):
        webbrowser.open("https://github.com/hdchan/R4-MG/releases")