from PyQt5.QtWidgets import QMainWindow

from AppCore.Config.ConfigurationManager import *
from AppUI.AppDependenciesProviding import AppDependenciesProviding
from AppUI.Configuration.AppUIConfiguration import *
from AppUI.UIComponents import AppUIConfigurationCheckableR4UIActionMenuItem
from R4UI import MenuListBuilder, R4UIActionMenuItem, R4UIMenuBarBuilder


class AppMenuBarBuilder:
    def __init__(self, app_dependencies_provider: AppDependenciesProviding):
        self._app_dependencies_provider = app_dependencies_provider
        self._router = app_dependencies_provider.router
        self._external_app_dependencies_provider = app_dependencies_provider.external_app_dependencies_provider
        self._data_source_draft_list = app_dependencies_provider.data_source_draft_list
        self._configuration_manager = app_dependencies_provider.configuration_manager
    
    
    def build_draft_list_menu_bar(self, window: QMainWindow) -> R4UIMenuBarBuilder:
        def _export_to_swudb():
            try:
                self._external_app_dependencies_provider.export_draft_list(self._data_source_draft_list.draft_packs, self._configuration_manager.configuration.picture_dir_path, True)
            except Exception as error:
                self._router.show_error(error)
        
        def _prompt_keeep_packs_clear_list():
            if self._router.prompt_accept("Clear list BUT keep packs", "This will keep packs, but clear their individual lists. Do you want to proceed?"):
                self._data_source_draft_list.keep_packs_clear_lists()
        
        def _prompt_clear_list():
            if self._router.prompt_accept("Clear ENTIRE list", "This removes ALL packs. Do you want to proceed?"):
                self._data_source_draft_list.clear_entire_draft_list()
        
        def _set_image_preview_enabled(mutable_config: MutableAppUIConfiguration, old_config: AppUIConfiguration):
            mutable_config.core_mutable_configuration.set_is_draft_list_image_preview_enabled(not old_config.core_configuration.is_draft_list_image_preview_enabled)
        
        return R4UIMenuBarBuilder([
                MenuListBuilder(
                    "File",
                    [
                        R4UIActionMenuItem(
                            "Export",
                            _export_to_swudb
                            ),
                        R4UIActionMenuItem(
                            "Settings",
                            lambda: self._router.open_draft_list_settings_page()
                            ),
                        
                    ]  
                ),
                MenuListBuilder(
                    "Actions",[
                        R4UIActionMenuItem(
                            "Clear list BUT keep packs",
                            _prompt_keeep_packs_clear_list
                            ),
                        R4UIActionMenuItem(
                            "Clear ENTIRE list",
                            _prompt_clear_list
                            ),
                    ]),
                MenuListBuilder(
                    "Toggles",[
                        AppUIConfigurationCheckableR4UIActionMenuItem(
                            self._app_dependencies_provider,
                            "Draft list image preview", 
                            lambda x: x.core_configuration.is_draft_list_image_preview_enabled, 
                            _set_image_preview_enabled
                            ),
                        ]),
                MenuListBuilder(
                    "Windows",[
                        R4UIActionMenuItem(
                            "Image Deployer",
                            self._router.open_image_deployment_view
                            ),
                    ]),
                # MenuListBuilder(
                #     "Presentation View",[
                #         AppUIConfigurationCheckableR4UIActionMenuItem(
                #             app_dependencies_provider,
                #             "Aggregate", 
                #             lambda x: x.draft_list_styles.is_list_aggregated, 
                #             self._set_aggregate
                #             ),
                #     ])
                
            ]).set_to_window(window)
    
    
    
    # MARK: - actions
    def settings_action(self) -> R4UIActionMenuItem:
        return R4UIActionMenuItem("Settings", 
                              self._app_dependencies_provider, 
                              lambda: self._app_dependencies_provider.router.open_settings_page()) # type: ignore