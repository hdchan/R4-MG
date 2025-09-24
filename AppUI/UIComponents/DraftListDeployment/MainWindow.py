from AppUI.AppDependenciesProviding import AppDependenciesProviding
from AppUI.UIComponents.Base import AppWindow
from PyQtUI import ActionMenuItem, MenuBarBuilder, MenuListBuilder

from .DraftListDeployerSearchComboViewController import \
    DraftListDeployerSearchComboViewController


class MainWindow(AppWindow):
    def __init__(self, app_dependencies_provider: AppDependenciesProviding):
        super().__init__(app_dependencies_provider=app_dependencies_provider, 
                         central_widget=DraftListDeployerSearchComboViewController(app_dependencies_provider),
                         window_config_identifier="draft_list",
                         default_width=500, 
                         default_height=400)
        self._router = app_dependencies_provider.router
        self._data_source_draft_list = app_dependencies_provider.data_source_draft_list
        self._external_app_dependencies_provider = app_dependencies_provider.external_app_dependencies_provider
        self._observation_tower = app_dependencies_provider.observation_tower
        self._configuration_manager = app_dependencies_provider.configuration_manager
        # self.setWindowTitle("Draft List")
        
        menu_bar = MenuBarBuilder([
                MenuListBuilder(
                    "File",
                    [
                        ActionMenuItem(
                            "Export to SWUDB",
                            self._export_to_swudb
                            ),
                        # ActionMenuItem(
                        #     "Export to MeleeGG",
                        #     lambda: self._external_app_dependencies_provider.export_draft_list(self._data_source_draft_list.draft_packs, self._configuration_manager.configuration.picture_dir_path, False)
                        #     ),
                        # ActionMenuItem(
                        #     "Export to CSV",
                        #     lambda: self._external_app_dependencies_provider.export_draft_list_csv(self._data_source_draft_list.draft_packs, self._configuration_manager.configuration.picture_dir_path)
                        #     ),
                        ActionMenuItem(
                            "Settings",
                            lambda: app_dependencies_provider.router.open_draft_list_settings_page()
                            ),
                        
                    ]  
                ),
                MenuListBuilder(
                    "Actions",[
                        ActionMenuItem(
                            "Clear list BUT keep packs",
                            self._prompt_keeep_packs_clear_list
                            ),
                        ActionMenuItem(
                            "Clear ENTIRE list",
                            self._prompt_clear_list
                            ),
                    ]),
                
                # MenuListBuilder(
                #     "Presentation View",[
                #         AppUIConfigurationCheckableActionMenuItem(
                #             app_dependencies_provider,
                #             "Aggregate", 
                #             lambda x: x.draft_list_styles.is_list_aggregated, 
                #             self._set_aggregate
                #             ),
                #     ])
                
            ])
        menu_bar.setParent(self)
        menu_bar.setNativeMenuBar(False)
        self.setMenuBar(menu_bar)
    
    def _export_to_swudb(self):
        try:
            self._external_app_dependencies_provider.export_draft_list(self._data_source_draft_list.draft_packs, self._configuration_manager.configuration.picture_dir_path, True)
        except Exception as error:
            self._router.show_error(error)
    
    def _prompt_keeep_packs_clear_list(self):
        if self._router.prompt_accept("Clear list BUT keep packs", "This will keep packs, but clear their individual lists. Do you want to proceed?"):
            self._data_source_draft_list.keep_packs_clear_lists()
    
    def _prompt_clear_list(self):
        if self._router.prompt_accept("Clear ENTIRE list", "This removes ALL packs. Do you want to proceed?"):
            self._data_source_draft_list.clear_entire_draft_list()