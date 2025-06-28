from typing import Callable

from PyQt5.QtWidgets import QAction, QMenu, QMenuBar

from AppCore.Config.ConfigurationManager import *
from AppCore.Service import PlatformServiceProtocol
from AppUI.AppDependenciesProviding import AppDependenciesProviding


class ImageDeploymentMenuBar(QMenuBar):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesProviding):
        super().__init__()
        self._configuration_manager = app_dependencies_provider.configuration_manager
        self._platform_service_provider = app_dependencies_provider.platform_service_provider
        self._router = app_dependencies_provider.router
        self._data_source_image_resource_deployer = app_dependencies_provider.data_source_image_resource_deployer
        self._external_app_dependencies_provider = app_dependencies_provider.external_app_dependencies_provider
        self.build_menu_bar()
        
        self.bind_new_file(lambda: self._router.prompt_generate_new_file_with_placeholder(self._external_app_dependencies_provider.card_back_image_path))
        self.bind_open_settings_page(self._router.open_app_settings_page)
        self.bind_open_about_page(self._router.open_about_page)
        self.bind_unstage_all_staging_resources(self._router.confirm_unstage_all_resources)
        self.bind_clear_cache_dir(self._router.confirm_clear_cache)
        self.bind_open_update_page(self._router.open_update_page)
        self.bind_open_shortcuts_page(self._router.open_shortcuts_page)
        self.bind_open_manage_deck_list_page(self._router.open_manage_deck_list_page)
        self.bind_refresh_production_images(self._data_source_image_resource_deployer.load_production_resources)
        
    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration

    @property
    def _platform_service(self) -> PlatformServiceProtocol:
        return self._platform_service_provider.platform_service

    def build_menu_bar(self):
        # MARK: - # File
        self._file_menu = QMenu("&File")
        self.addMenu(self._file_menu)

        self._new_file_menu = QAction('New image file')
        self._file_menu.addAction(self._new_file_menu) # type: ignore

        self._refresh_production_images = QAction('Refresh production images')
        self._file_menu.addAction(self._refresh_production_images) # type: ignore
        
        self._open_production_dir = QAction('Open image directory')
        self._open_production_dir.triggered.connect(self.did_open_production_dir)
        self._file_menu.addAction(self._open_production_dir) # type: ignore
        
        self._settings_menu = QAction("Settings")
        self._file_menu.addAction(self._settings_menu) # type: ignore
        
        
        
        # MARK: - # Actions
        self._action_menu = QMenu("&Action")
        self.addMenu(self._action_menu)

        self._unstage_all_staging_resources = QAction('Unstage all staged resources')
        self._action_menu.addAction(self._unstage_all_staging_resources) # type: ignore

        self._clear_cache_dir = QAction('Clear cache')
        self._action_menu.addAction(self._clear_cache_dir) # type: ignore

        
        
        
        # MARK: - # View
        self._view_menu = QMenu("&View")
        self.addMenu(self._view_menu)
        
        self._show_resource_details = QAction('Show resource details')
        self._show_resource_details.triggered.connect(self.did_toggle_show_resource_details)
        self._show_resource_details.setCheckable(True)
        self._show_resource_details.setChecked(self._configuration.show_resource_details)
        self._view_menu.addAction(self._show_resource_details) # type: ignore
        
        
        self._hide_image_preview = QAction('Hide image preview')
        self._hide_image_preview.triggered.connect(self.did_toggle_hide_image_preview)
        self._hide_image_preview.setCheckable(True)
        self._hide_image_preview.setChecked(self._configuration.hide_image_preview)
        self._view_menu.addAction(self._hide_image_preview) # type: ignore
        
        # MARK: - ## Image preview scale
        self._image_preview_scale = QMenu('Image preview scale')
        self._view_menu.addMenu(self._image_preview_scale)

        self._image_preview_scale_25 = QAction('25%')
        self._image_preview_scale_25.triggered.connect(self.did_toggle_image_preview_scale_25)
        self._image_preview_scale_25.setCheckable(True)
        self._image_preview_scale.addAction(self._image_preview_scale_25) # type: ignore

        self._image_preview_scale_50 = QAction('50%')
        self._image_preview_scale_50.triggered.connect(self.did_toggle_image_preview_scale_50)
        self._image_preview_scale_50.setCheckable(True)
        self._image_preview_scale.addAction(self._image_preview_scale_50) # type: ignore
        
        self._image_preview_scale_75 = QAction('75%')
        self._image_preview_scale_75.triggered.connect(self.did_toggle_image_preview_scale_75)
        self._image_preview_scale_75.setCheckable(True)
        self._image_preview_scale.addAction(self._image_preview_scale_75) # type: ignore
        
        self._image_preview_scale_100 = QAction('100%')
        self._image_preview_scale_100.triggered.connect(self.did_toggle_image_preview_scale_100)
        self._image_preview_scale_100.setCheckable(True)
        self._image_preview_scale.addAction(self._image_preview_scale_100) # type: ignore
        
        self._sync_image_preview_scale_checkmarks()


        self._hide_deployment_cell_controls = QAction('Hide deployment cell controls')
        self._hide_deployment_cell_controls.triggered.connect(self.did_toggle_hide_deployment_cell_controls)
        self._hide_deployment_cell_controls.setCheckable(True)
        self._hide_deployment_cell_controls.setChecked(self._configuration.hide_deployment_cell_controls)
        self._view_menu.addAction(self._hide_deployment_cell_controls) # type: ignore



        # MARK: - ## Card details
        self._card_title_detail = QMenu('Card title detail')
        self._view_menu.addMenu(self._card_title_detail)

        self._card_title_detail_short = QAction('Short')
        self._card_title_detail_short.triggered.connect(self.did_toggle_card_title_detail_short)
        self._card_title_detail_short.setCheckable(True)
        self._card_title_detail.addAction(self._card_title_detail_short) # type: ignore

        self._card_title_detail_normal = QAction('Normal')
        self._card_title_detail_normal.triggered.connect(self.did_toggle_card_title_detail_normal)
        self._card_title_detail_normal.setCheckable(True)
        self._card_title_detail.addAction(self._card_title_detail_normal) # type: ignore

        self._card_title_detail_detailed = QAction('Detailed')
        self._card_title_detail_detailed.triggered.connect(self.did_toggle_card_title_detail_detailed)
        self._card_title_detail_detailed.setCheckable(True)
        self._card_title_detail.addAction(self._card_title_detail_detailed) # type: ignore

        self._sync_card_title_detail_checkmarks()



        # MARK: - ## Deployment list sort order
        self._sort_deployment_list_menu = QMenu('Sort deployment list')
        self._view_menu.addMenu(self._sort_deployment_list_menu)
        
        # MARK: - ### Criteria
        self._sort_deployment_list_criteria = QMenu('Criteria')
        self._sort_deployment_list_menu.addMenu(self._sort_deployment_list_criteria)
        
        self._sort_deployment_list_criteria_file_name = QAction('File name')
        self._sort_deployment_list_criteria_file_name.triggered.connect(self.did_toggle_sort_deployment_list_criteria_file_name)
        self._sort_deployment_list_criteria_file_name.setCheckable(True)
        self._sort_deployment_list_criteria.addAction(self._sort_deployment_list_criteria_file_name) # type: ignore
        
        self._sort_deployment_list_criteria_created_date = QAction('Created date')
        self._sort_deployment_list_criteria_created_date.triggered.connect(self.did_toggle_sort_deployment_list_criteria_created_date)
        self._sort_deployment_list_criteria_created_date.setCheckable(True)
        self._sort_deployment_list_criteria.addAction(self._sort_deployment_list_criteria_created_date) # type: ignore
        
        self._sync_sort_deployment_list_criteria()
        
        # MARK: - ### Order
        self._sort_deployment_list_order = QMenu('Order')
        self._sort_deployment_list_menu.addMenu(self._sort_deployment_list_order)
    
        self._sort_deployment_list_order_asc = QAction('Ascending')
        self._sort_deployment_list_order_asc.triggered.connect(self.did_toggle_sort_deployment_list_order_asc)
        self._sort_deployment_list_order_asc.setCheckable(True)
        self._sort_deployment_list_order.addAction(self._sort_deployment_list_order_asc) # type: ignore
        
        self._sort_deployment_list_order_desc = QAction('Descending')
        self._sort_deployment_list_order_desc.triggered.connect(self.did_toggle_sort_deployment_list_order_desc)
        self._sort_deployment_list_order_desc.setCheckable(True)
        self._sort_deployment_list_order.addAction(self._sort_deployment_list_order_desc) # type: ignore
        
        self._sync_sort_deployment_list_order()
    
        # MARK: - ## Deployment List Orientation 
        self._is_deployment_list_horizontal = QAction('Horizontal deployment list')
        self._is_deployment_list_horizontal.triggered.connect(self.did_toggle_is_deployment_list_horizontal)
        self._is_deployment_list_horizontal.setCheckable(True)
        self._is_deployment_list_horizontal.setChecked(self._configuration.is_deployment_list_horizontal)
        self._view_menu.addAction(self._is_deployment_list_horizontal) # type: ignore
    
        # MARK: - ## Window size
        self._reset_window_size = QAction('Reset window size')
        self._reset_window_size.triggered.connect(self.did_toggle_reset_window_size)
        self._view_menu.addAction(self._reset_window_size) # type: ignore

        # MARK: - Tools
        self._tool_menu = QMenu("&Tools")
        self.addMenu(self._tool_menu)
        
        self._manage_deck_list_action = QAction('Manage set list')
        self._tool_menu.addAction(self._manage_deck_list_action) # type: ignore
        
        # MARK: - About
        self._help_menu = QMenu("&Help")
        self.addMenu(self._help_menu)
        
        self._shortcuts_list_action = QAction('Quick Guide')
        self._help_menu.addAction(self._shortcuts_list_action) # type: ignore


        self._check_update = QAction('Check for updates')
        self._help_menu.addAction(self._check_update) # type: ignore

        self._about_action = QAction("About")
        self._help_menu.addAction(self._about_action) # type: ignore

        # MARK: - Developer
        if self._configuration.is_developer_mode:
            self._developer_menu = QMenu("&Developer")
            self.addMenu(self._developer_menu)

            self._open_configuration_dir = QAction('Reveal configuration in file explorer')
            self._open_configuration_dir.triggered.connect(self.did_open_configuration_dir)
            self._developer_menu.addAction(self._open_configuration_dir) # type: ignore

            self._open_temp_dir = QAction('Reveal app data folder in file explorer')
            self._open_temp_dir.triggered.connect(self.did_open_app_data_dir)
            self._developer_menu.addAction(self._open_temp_dir) # type: ignore

            self._mock_data_mode = QAction('Mock data')
            self._mock_data_mode.triggered.connect(self.did_toggle_mock_data_mode)
            self._mock_data_mode.setCheckable(True)
            self._mock_data_mode.setChecked(self._configuration.is_mock_data)
            self._developer_menu.addAction(self._mock_data_mode) # type: ignore
            
            self._delay_network_mode = QAction('Delay network call')
            self._delay_network_mode.triggered.connect(self.did_toggle_delay_network_mode)
            self._delay_network_mode.setCheckable(True)
            self._delay_network_mode.setChecked(self._configuration.is_delay_network_mode)
            self._developer_menu.addAction(self._delay_network_mode) # type: ignore
            
            
            self._download_remote_asset = QAction('Open cache')
            self._download_remote_asset.triggered.connect(self.did_toggle_download_remote_asset)
            self._developer_menu.addAction(self._download_remote_asset) # type: ignore

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
        
    def bind_open_update_page(self, fn: Callable[[], None]):\
        self._check_update.triggered.connect(fn)
        
    def bind_open_shortcuts_page(self, fn: Callable[[], None]):
        self._shortcuts_list_action.triggered.connect(fn)
        
    def bind_open_manage_deck_list_page(self, fn: Callable[[], None]):
        self._manage_deck_list_action.triggered.connect(fn)

    # MARK: - actions
    def did_toggle_show_resource_details(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_show_resource_details(is_on)
        self._configuration_manager.save_configuration(new_config)

    
    def did_toggle_hide_image_preview(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_hide_image_preview(is_on)
        self._configuration_manager.save_configuration(new_config)

    # Image preview scale
    def did_toggle_image_preview_scale_25(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_image_preview_scale(0.25)
        self._configuration_manager.save_configuration(new_config)
        self._sync_image_preview_scale_checkmarks()
        
    def did_toggle_image_preview_scale_50(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_image_preview_scale(0.5)
        self._configuration_manager.save_configuration(new_config)
        self._sync_image_preview_scale_checkmarks()
        
    def did_toggle_image_preview_scale_75(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_image_preview_scale(0.75)
        self._configuration_manager.save_configuration(new_config)
        self._sync_image_preview_scale_checkmarks()
        
    def did_toggle_image_preview_scale_100(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_image_preview_scale(1.0)
        self._configuration_manager.save_configuration(new_config)
        self._sync_image_preview_scale_checkmarks()

    def _sync_image_preview_scale_checkmarks(self):
        preference = self._configuration.image_preview_scale
        # TODO: change preferences to encoded ints
        self._image_preview_scale_25.setChecked(preference == 0.25)
        self._image_preview_scale_50.setChecked(preference == 0.5)
        self._image_preview_scale_75.setChecked(preference == 0.75)
        self._image_preview_scale_100.setChecked(preference == 1.0)
        
        
    def did_toggle_hide_deployment_cell_controls(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_hide_deployment_cell_controls(is_on)
        self._configuration_manager.save_configuration(new_config)
    
    
    # Card title detail
    
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
        
    def _sync_card_title_detail_checkmarks(self):
        preference = self._configuration.card_title_detail
        self._card_title_detail_short.setChecked(preference == Configuration.Settings.CardTitleDetail.SHORT)
        self._card_title_detail_normal.setChecked(preference == Configuration.Settings.CardTitleDetail.NORMAL)
        self._card_title_detail_detailed.setChecked(preference == Configuration.Settings.CardTitleDetail.DETAILED)
        

    def did_toggle_sort_deployment_list_criteria_file_name(self):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_deployment_list_sort_criteria(Configuration.Settings.DeploymentListSortCriteria.FILE_NAME)
        self._configuration_manager.save_configuration(new_config)
        self._sync_sort_deployment_list_criteria()
        
    def did_toggle_sort_deployment_list_criteria_created_date(self):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_deployment_list_sort_criteria(Configuration.Settings.DeploymentListSortCriteria.CREATED_DATE)
        self._configuration_manager.save_configuration(new_config)
        self._sync_sort_deployment_list_criteria()

    def _sync_sort_deployment_list_criteria(self):
        preference = self._configuration.deployment_list_sort_criteria
        self._sort_deployment_list_criteria_file_name.setChecked(preference == Configuration.Settings.DeploymentListSortCriteria.FILE_NAME)
        self._sort_deployment_list_criteria_created_date.setChecked(preference == Configuration.Settings.DeploymentListSortCriteria.CREATED_DATE)

    def did_toggle_sort_deployment_list_order_asc(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_deployment_list_sort_order(False)
        self._configuration_manager.save_configuration(new_config)
        self._sync_sort_deployment_list_order()
        
    def did_toggle_sort_deployment_list_order_desc(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_deployment_list_sort_order(True)
        self._configuration_manager.save_configuration(new_config)
        self._sync_sort_deployment_list_order()
        
    def _sync_sort_deployment_list_order(self):
        is_desc_order = self._configuration.deployment_list_sort_is_desc_order
        self._sort_deployment_list_order_asc.setChecked(not is_desc_order)
        self._sort_deployment_list_order_desc.setChecked(is_desc_order)
        
    def did_toggle_is_deployment_list_horizontal(self, is_horizontal: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_is_deployment_list_horizontal(is_horizontal)
        self._configuration_manager.save_configuration(new_config)

    def did_toggle_reset_window_size(self):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.reset_window_size()
        self._configuration_manager.save_configuration(new_config)
    
    

    def did_open_production_dir(self):
        self._platform_service.open_file(self._configuration.picture_dir_path)

    
        
        
    # MARK: - developer
    def did_open_configuration_dir(self):
        self._platform_service.open_file(self._configuration.config_directory)

    def did_open_app_data_dir(self):
        self._platform_service.open_file(self._configuration.assets_dir_path)

    def did_toggle_download_remote_asset(self):
        self._platform_service.open_file(self._configuration.cache_dir_path)

    def did_toggle_mock_data_mode(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_is_mock_data(is_on)
        self._configuration_manager.save_configuration(new_config)

    def did_toggle_delay_network_mode(self, is_on: bool):
        new_config = self._configuration_manager.mutable_configuration()
        new_config.set_is_delay_network_mode(is_on)
        self._configuration_manager.save_configuration(new_config)