
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow

from AppUI.AppDependenciesProviding import AppDependenciesProviding
from AppUI.Configuration.AppUIConfiguration import (AppUIConfiguration,
                                                    MutableAppUIConfiguration)
from AppUI.UIComponents import AppUIConfigurationCheckableActionMenuItem
from PyQtUI import ActionMenuItem, MenuBarBuilder, MenuListBuilder

from .DraftListDeployerSearchComboViewController import \
    DraftListDeployerSearchComboViewController


class MainWindow(QMainWindow):
    def __init__(self, app_dependencies_provider: AppDependenciesProviding):
        super().__init__()
        self._router = app_dependencies_provider.router
        self._data_source_draft_list = app_dependencies_provider.data_source_draft_list
        self._external_app_dependencies_provider = app_dependencies_provider.external_app_dependencies_provider
        self._configuration_manager = app_dependencies_provider.configuration_manager
        # self.setWindowTitle("Draft List")
        
        menu_bar = MenuBarBuilder([
                MenuListBuilder(
                    "File",
                    [
                        ActionMenuItem(
                            "Export to SWUDB",
                            lambda: self._external_app_dependencies_provider.export_draft_list(self._data_source_draft_list.draft_packs, self._configuration_manager.configuration.picture_dir_path, True)
                            ),
                        ActionMenuItem(
                            "Export to MeleeGG",
                            lambda: self._external_app_dependencies_provider.export_draft_list(self._data_source_draft_list.draft_packs, self._configuration_manager.configuration.picture_dir_path, False)
                            ),
                        ActionMenuItem(
                            "Export to CSV",
                            lambda: self._external_app_dependencies_provider.export_draft_list_csv(self._data_source_draft_list.draft_packs, self._configuration_manager.configuration.picture_dir_path)
                            ),
                        ActionMenuItem(
                            "Settings",
                            lambda: app_dependencies_provider.router.open_draft_list_settings_page(self)
                            ),
                        
                    ]  
                ),
                MenuListBuilder(
                    "Actions",[
                        ActionMenuItem(
                            "Keep packs and clear list",
                            self._prompt_keeep_packs_clear_list
                            ),
                        ActionMenuItem(
                            "Clear all list",
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
        
        self.central_widget = DraftListDeployerSearchComboViewController(app_dependencies_provider)
        self.setCentralWidget(self.central_widget)
        
        centerPoint = QDesktopWidget().availableGeometry().center()
        self.setGeometry(0, 0, 900, 400)
        qtRectangle = self.frameGeometry()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
    
    def _prompt_keeep_packs_clear_list(self):
        if self._router.prompt_accept("Keep packs and clear list", "This will keep packs, but clear their individual lists. Do you want to proceed?"):
            self._data_source_draft_list.keep_packs_clear_lists()
    
    def _prompt_clear_list(self):
        if self._router.prompt_accept("Clear entire list", "This removes ALL packs. Do you want to proceed?"):
            self._data_source_draft_list.clear_entire_draft_list()
        
    # def _set_aggregate(self, new_config: MutableAppUIConfiguration, old_config: AppUIConfiguration):
    #     # TODO: create convenience wrapper?
    #     new_config.draft_list_styles.set_is_list_aggregated(not old_config.draft_list_styles.is_list_aggregated)
    #     new_config.set_draft_list_styles(new_config.draft_list_styles)