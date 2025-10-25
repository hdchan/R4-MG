from PySide6.QtWidgets import QMainWindow
from typing import Optional
from AppCore.Config.ConfigurationManager import *
from AppCore.Service.PlatformServiceProvider import PlatformServiceProtocol
from AppUI.AppDependenciesInternalProviding import AppDependenciesInternalProviding
from AppUI.Configuration.AppUIConfiguration import *
from AppUI.UIComponents import AppUIConfigurationCheckableRActionMenuItem
from R4UI import RActionMenuItem, RMenuBarBuilder, RMenuListBuilder
import copy

class AppMenuBarBuilder:
    def __init__(self, app_dependencies_provider: AppDependenciesInternalProviding):
        self._app_dependencies_provider = app_dependencies_provider
        self._router = app_dependencies_provider.router
        self._external_app_dependencies_provider = app_dependencies_provider.external_app_dependencies_provider
        self._data_source_draft_list = app_dependencies_provider.data_source_draft_list
        self._app_ui_configuration_manager = app_dependencies_provider.app_ui_configuration_manager
        self._platform_service_provider = app_dependencies_provider.platform_service_provider
        self._data_source_image_resource_deployer = app_dependencies_provider.data_source_image_resource_deployer

    @property
    def _platform_service(self) -> PlatformServiceProtocol:
        return self._platform_service_provider.platform_service
    
    @property
    def _core_configuration(self) -> Configuration:
        return self._app_ui_configuration_manager.configuration.core_configuration

    def build_shared_actions_menu(self) -> RMenuListBuilder:
        def confirm_clear_cache():
            if self._router.prompt_accept("Clear cache", "Are you sure you want to clear the cache?"):
                self._platform_service_provider.platform_service.clear_cache()

        return RMenuListBuilder("Actions") \
        .add_actions([
            RActionMenuItem("Clear cache", confirm_clear_cache),
        ])
    
    def build_draft_list_menu_bar(self, window: QMainWindow) -> RMenuBarBuilder:
        return RMenuBarBuilder([
                self.draft_list_actions_menu(),
                self.image_preview_view_toggle_menu(),
            ]) \
            .set_to_window(window) \
            .add_menus(self.shared_menu_bar_items(initial_settings_tab_index=1))

    def build_image_deployment_menu_bar(self, window: QMainWindow) -> RMenuBarBuilder:
        def confirm_unstage_all_resources():
            if self._router.prompt_accept("Unstage all staged resources", "Are you sure you want to unstage all staged resources?"):
                self._data_source_image_resource_deployer.unstage_all_resources()
        
        def prompt_generate_new_file_with_placeholder(placeholder_image_path: Optional[str]):
            file_name, ok = self._router.prompt_text_input('Create new image file', 'Enter file name:')
            if ok:
                try:
                    self._data_source_image_resource_deployer.generate_new_file(file_name, placeholder_image_path)
                    self._data_source_image_resource_deployer.load_production_resources()
                except Exception as error:
                    self._router.show_error(error)

        return RMenuBarBuilder([
                self.build_shared_actions_menu() \
                    .add_separator() \
                    .add_actions([
                        RActionMenuItem("New image file", lambda: prompt_generate_new_file_with_placeholder(self._external_app_dependencies_provider.card_back_image_path)),
                        RActionMenuItem("Refresh production images", self._data_source_image_resource_deployer.load_production_resources),
                        RActionMenuItem("Unstage all staged resources", confirm_unstage_all_resources),
                    ]),
                self.image_preview_view_toggle_menu() \
                    .add_separator() \
                    .add_actions([
                        AppUIConfigurationCheckableRActionMenuItem(
                            self._app_dependencies_provider,
                            "Hide image deployment controls", 
                            lambda x: x.core_configuration.hide_deployment_cell_controls, 
                            lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_hide_deployment_cell_controls(not old_config.core_configuration.hide_deployment_cell_controls)
                            ),
                        AppUIConfigurationCheckableRActionMenuItem(
                            self._app_dependencies_provider,
                            "Horizontal deployment list", 
                            lambda x: x.core_configuration.is_deployment_list_horizontal, 
                            lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_is_deployment_list_horizontal(not old_config.core_configuration.is_deployment_list_horizontal)
                            ),
                    ]) \
                    .add_menus([
                        RMenuListBuilder("Sort deployment list") \
                            .add_menus([
                                RMenuListBuilder("Criteria", [
                                    AppUIConfigurationCheckableRActionMenuItem(
                                        self._app_dependencies_provider,
                                        "Created date", 
                                        lambda x: x.core_configuration.deployment_list_sort_criteria == Configuration.Settings.DeploymentListSortCriteria.CREATED_DATE, 
                                        lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_deployment_list_sort_criteria(Configuration.Settings.DeploymentListSortCriteria.CREATED_DATE)
                                        ),

                                    AppUIConfigurationCheckableRActionMenuItem(
                                        self._app_dependencies_provider,
                                        "File name", 
                                        lambda x: x.core_configuration.deployment_list_sort_criteria == Configuration.Settings.DeploymentListSortCriteria.FILE_NAME, 
                                        lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_deployment_list_sort_criteria(Configuration.Settings.DeploymentListSortCriteria.FILE_NAME)
                                        ),
                                ]),
                                RMenuListBuilder("Order", [
                                    AppUIConfigurationCheckableRActionMenuItem(
                                        self._app_dependencies_provider,
                                        "Ascending", 
                                        lambda x: not x.core_configuration.deployment_list_sort_is_desc_order, 
                                        lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_deployment_list_sort_order(False)
                                        ),
                                    AppUIConfigurationCheckableRActionMenuItem(
                                        self._app_dependencies_provider,
                                        "Descending", 
                                        lambda x: x.core_configuration.deployment_list_sort_is_desc_order, 
                                        lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_deployment_list_sort_order(True)
                                        ),
                                ]),
                            ]),
                    ]),
            ]) \
            .set_to_window(window) \
            .add_menus(self.shared_menu_bar_items(initial_settings_tab_index=0))

    def shared_menu_bar_items(self, initial_settings_tab_index: int = 0) -> List[Optional[RMenuListBuilder]]:
        return [
            self.windows_menu(),
            self.help_menu(initial_settings_tab_index),
            self.developer_menu()
        ]

    def image_preview_view_toggle_menu(self):
        return RMenuListBuilder("View") \
        .add_menus([
            RMenuListBuilder("Card title detail",[
                AppUIConfigurationCheckableRActionMenuItem(
                    self._app_dependencies_provider,
                    "Short", 
                    lambda x: x.core_configuration.card_title_detail == Configuration.Settings.CardTitleDetail.SHORT, 
                    lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_card_title_detail(Configuration.Settings.CardTitleDetail.SHORT)
                    ),
                AppUIConfigurationCheckableRActionMenuItem(
                    self._app_dependencies_provider,
                    "Normal", 
                    lambda x: x.core_configuration.card_title_detail == Configuration.Settings.CardTitleDetail.NORMAL, 
                    lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_card_title_detail(Configuration.Settings.CardTitleDetail.NORMAL)
                    ),
                AppUIConfigurationCheckableRActionMenuItem(
                    self._app_dependencies_provider,
                    "Detailed", 
                    lambda x: x.core_configuration.card_title_detail == Configuration.Settings.CardTitleDetail.DETAILED, 
                    lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_card_title_detail(Configuration.Settings.CardTitleDetail.DETAILED)
                    ),
            ]),
        ]) \
        .add_actions([
            AppUIConfigurationCheckableRActionMenuItem(
                    self._app_dependencies_provider,
                    "Hide image preview", 
                    lambda x: x.core_configuration.hide_image_preview, 
                    lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_hide_image_preview(not old_config.core_configuration.hide_image_preview)
                    ),
        ]) \
        .add_menus([
            RMenuListBuilder("Image preview scale",[
                AppUIConfigurationCheckableRActionMenuItem(
                    self._app_dependencies_provider,
                    "25%", 
                    lambda x: x.core_configuration.image_preview_scale == 0.25, 
                    lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_image_preview_scale(0.25)
                    ),
                AppUIConfigurationCheckableRActionMenuItem(
                    self._app_dependencies_provider,
                    "50%", 
                    lambda x: x.core_configuration.image_preview_scale == 0.5, 
                    lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_image_preview_scale(0.5)
                    ),
                AppUIConfigurationCheckableRActionMenuItem(
                    self._app_dependencies_provider,
                    "75%", 
                    lambda x: x.core_configuration.image_preview_scale == 0.75, 
                    lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_image_preview_scale(0.75)
                    ),
                AppUIConfigurationCheckableRActionMenuItem(
                    self._app_dependencies_provider,
                    "100%", 
                    lambda x: x.core_configuration.image_preview_scale == 1.0, 
                    lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_image_preview_scale(1.0)
                    ),
            ]),
        ]) \
        .add_actions([
            AppUIConfigurationCheckableRActionMenuItem(
                    self._app_dependencies_provider,
                    "Show resource details", 
                    lambda x: x.core_configuration.show_resource_details, 
                    lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_show_resource_details(not old_config.core_configuration.show_resource_details)
                    ),
        ]) \
        

    def draft_list_actions_menu(self):
        def _export_draft_list():
            try:
                self._external_app_dependencies_provider.export_draft_list()
            except Exception as error:
                self._router.show_error(error)

        def _import_draft_list():
            try:
                self._external_app_dependencies_provider.import_draft_list()
            except Exception as error:
                self._router.show_error(error)
        
        
        def _prompt_keeep_packs_clear_list():
            if self._router.prompt_accept("Clear list BUT keep packs", 
                                          "This will keep packs, but clear their individual lists. Do you want to proceed?"):
                self._data_source_draft_list.keep_packs_clear_lists()
        
        def _prompt_clear_list():
            if self._router.prompt_accept("Clear ENTIRE list", 
                                          "This removes ALL packs. Do you want to proceed?"):
                self._data_source_draft_list.clear_entire_draft_list()

        return self.build_shared_actions_menu() \
            .add_separator() \
            .add_actions([
                RActionMenuItem("Export draft list",
                                    _export_draft_list),
                RActionMenuItem("Import",
                                    _import_draft_list),
            ]) \
            .add_actions([
                RActionMenuItem("Clear list BUT keep packs",
                                    _prompt_keeep_packs_clear_list),
                RActionMenuItem("Clear ENTIRE list", 
                                    _prompt_clear_list),
            ])
    
    def toggles_menu(self) -> RMenuListBuilder:
        return RMenuListBuilder("Toggles",[
                AppUIConfigurationCheckableRActionMenuItem(
                    self._app_dependencies_provider,
                    "Draft list image preview", 
                    lambda x: x.core_configuration.is_draft_list_image_preview_enabled, 
                    lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_is_draft_list_image_preview_enabled(not old_config.core_configuration.is_draft_list_image_preview_enabled)
                    ),
                    ])

    def windows_menu(self) -> RMenuListBuilder:
        return RMenuListBuilder("Windows",) \
            .add_actions([
                RActionMenuItem("Manage set list", self._router.open_manage_deck_list_page),
            ]) \
            .add_separator() \
            .add_actions([
                RActionMenuItem("Draft list deployer", self._router.open_draft_list_deployment_view),
                RActionMenuItem("Draft list image preview", self._router.open_draft_list_image_preview_view),
                RActionMenuItem("Image deployer", self._router.open_image_deployment_view),
            ]) \
            .add_separator() \
            .add_actions([
                RActionMenuItem("Cache directory",
                                   lambda: self._platform_service.open_file(self._core_configuration.cache_dir_path)),
                
                RActionMenuItem("Configuration file directory",
                                   lambda: self._platform_service.open_file(self._core_configuration.config_directory)),

                RActionMenuItem("Image deployment directory",
                                   lambda: self._platform_service.open_file(self._core_configuration.picture_dir_path)),
                
                RActionMenuItem("Logs directory",
                                   lambda: self._platform_service.open_file(self._core_configuration.logs_dir_path)),
            ])

    def help_menu(self, initial_settings_tab_index: int = 0) -> RMenuListBuilder:
        return RMenuListBuilder("Help") \
            .add_actions([
                RActionMenuItem("Settings", lambda: self._router.open_app_settings_page(initial_settings_tab_index)),
                RActionMenuItem("Quick guide", self._router.open_shortcuts_page),
            ]) \
            .add_separator() \
            .add_actions([
                
                RActionMenuItem("Check for updates", self._router.open_update_page),
                RActionMenuItem("About", self._router.open_about_page),
            ])

    def developer_menu(self) -> Optional[RMenuListBuilder]:
        if self._core_configuration.is_developer_mode == False:
            return None

        result_menu = RMenuListBuilder("Developer",[
                AppUIConfigurationCheckableRActionMenuItem(
                    self._app_dependencies_provider,
                    "Mock data", 
                    lambda x: x.core_configuration.is_mock_data, 
                    lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_is_mock_data(not old_config.core_configuration.is_mock_data)
                    ),

                AppUIConfigurationCheckableRActionMenuItem(
                    self._app_dependencies_provider,
                    "Delay network call", 
                    lambda x: x.core_configuration.is_delay_network_mode, 
                    lambda mutable_config, old_config: mutable_config.core_mutable_configuration.set_is_delay_network_mode(not old_config.core_configuration.is_delay_network_mode)
                    ), 
                    ])
        
        modifed_menu = self._external_app_dependencies_provider.hook_developer_menu(result_menu)
        if modifed_menu is not None:
            return modifed_menu
        
        return result_menu