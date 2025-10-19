
from typing import Optional

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import QTabWidget

from AppCore.Config import Configuration
from AppCore.Models import LocalResourceDataSourceProviding
from AppCore.Observation.Events import (ConfigurationUpdatedEvent,
                                        DraftPackUpdatedEvent,
                                        LocalCardResourceFetchEvent,
                                        LocalCardResourceSelectedFromDataSourceEvent,
                                        ProductionCardResourcesLoadEvent,
                                        PublishStagedCardResourcesEvent)
from AppCore.Observation.ObservationTower import *
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from R4UI import (BoldLabel, ComboBox, HorizontalBoxLayout, PushButton,
                  R4UIActionMenuItem, R4UIMenuListBuilder, RWidget,
                  VerticalBoxLayout)

from .DraftListTablePackPreviewViewController import (
    DraftListTablePackPreviewViewController,
    DraftListTablePackPreviewViewControllerDelegate)


class DraftListTabbedPackPreviewViewControllerDraftListTablePackPreviewViewControllerDelegate(DraftListTablePackPreviewViewControllerDelegate):
    def __init__(self, pack_identifier: str):
        self._pack_identifier = pack_identifier
    
    @property
    def dlp_pack_identifier(self) -> Optional[str]:
        return self._pack_identifier
    
    @property
    def dlp_is_presentation(self) -> bool:
        return False


class DraftListTabbedPackPreviewViewController(RWidget, TransmissionReceiverProtocol):
    def __init__(self, 
                 app_dependencies_provider: AppDependenciesInternalProviding,
                 data_source_local_resource_provider: LocalResourceDataSourceProviding):
        super().__init__()
        self._app_dependencies_provider = app_dependencies_provider
        self._data_source_draft_list = app_dependencies_provider.data_source_draft_list
        self._data_source_local_resource_provider = data_source_local_resource_provider
        self._data_source_image_resource_deployer = app_dependencies_provider.data_source_image_resource_deployer
        self._configuration_manager = app_dependencies_provider.configuration_manager
        self._router = app_dependencies_provider.router
        self._selected_tab = -1
        self._is_publishing = False
        self._setup_view()
        
        app_dependencies_provider.observation_tower.subscribe_multi(self, [DraftPackUpdatedEvent,
                                                                           LocalCardResourceFetchEvent,
                                                                           LocalCardResourceSelectedFromDataSourceEvent,
                                                                           ProductionCardResourcesLoadEvent, 
                                                                           ConfigurationUpdatedEvent, PublishStagedCardResourcesEvent])
        
        app_dependencies_provider.shortcut_action_coordinator.bind_add_card_to_draft_list(self._add_resource, self)
        
    def _setup_view(self):
        self._tab_widget = QTabWidget()
        tab_bar = self._tab_widget.tabBar()
        if tab_bar is not None:
            tab_bar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            tab_bar.customContextMenuRequested.connect(self._show_context_menu) # TODO: right clicking clicks tab, even if not switched to
        self._tab_widget.tabBarClicked.connect(self._tab_clicked)
        
        self._add_card_button = PushButton(None, self._add_resource)
        
        self._deployment_destination_selection = ComboBox()
        self._reset_deployment_destination_selection()
        
        VerticalBoxLayout([
            self._tab_widget,
            self._add_card_button,
            HorizontalBoxLayout([
                BoldLabel("Deployment Destination"),
                self._deployment_destination_selection,
                ]),
            
        ]).set_layout_to_widget(self)
        
        if self._data_source_draft_list.pack_list_count == 0:
            self._data_source_draft_list.create_new_pack()
        
        self._sync_ui()

    def _reset_deployment_destination_selection(self):
        try:
            # TODO: monitor this to ensure no memory leak
            self._deployment_destination_selection.disconnect()
        except:
            pass
        self._deployment_destination_selection.clear()
        self._deployment_destination_selection.addItems(
            ["None"] + [stuff.production_resource.file_name_with_ext for stuff in self._data_source_image_resource_deployer.deployment_resources])
        destination_string = self._configuration.draft_list_add_card_deployment_destination
        self._deployment_destination_selection.setCurrentText(destination_string)
        self._deployment_destination_selection.currentIndexChanged.connect(self._deployment_destination_selection_changed)

    def _deployment_destination_selection_changed(self, val: int):
        # if self._deployment_destination_selection.count() == 0:
        #     return
        # set and save config
        new_config = self._configuration_manager.mutable_configuration()
        destination_string: Optional[str] = None # first option is null
        if val > 0:
            destination_string = self._deployment_destination_selection.itemText(val)
        new_config.set_draft_list_add_card_deployment_destination(destination_string)
        self._configuration_manager.save_configuration(new_config)
        self._sync_ui()

    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration
    
    def _add_resource(self):
        # TODO: protect action when staging is enabled
        if self._is_publishing:
            return
        # print("got through!")
        selected_pack = self._tab_widget.currentIndex()
        selected_resource = self._data_source_local_resource_provider.data_source.selected_local_resource
        if selected_resource is not None:
            try:
                self._data_source_draft_list.add_resource_to_pack(selected_pack, selected_resource)
            except Exception as error:
                self._router.show_error(Exception(error))
                return
            
            destination_file_name = self._configuration.draft_list_add_card_deployment_destination
            if destination_file_name is None:
                return
            
            matching_deployment_resource = self._data_source_image_resource_deployer.deployment_resource_for_file_name(destination_file_name)
            
            if matching_deployment_resource is None:
                self._reset_deployment_destination_selection()
                return
            
            add_card_mode = self._configuration.draft_list_add_card_mode
            
            if add_card_mode == Configuration.Settings.DraftListAddCardMode.STAGE or add_card_mode == Configuration.Settings.DraftListAddCardMode.STAGE_AND_PUBLISH:
                self._data_source_image_resource_deployer.stage_resource(matching_deployment_resource, selected_resource)
            if add_card_mode == Configuration.Settings.DraftListAddCardMode.STAGE_AND_PUBLISH:
                try:
                    self._is_publishing = True
                    self._data_source_image_resource_deployer.publish_staged_resources()
                except Exception as error:
                    self._router.show_error(error)
                self._is_publishing = False
    
    # MARK: - Tab bar context menu
    def _tab_clicked(self, index: int):
        if index >= self._tab_widget.count() - 1:
            self._data_source_draft_list.create_new_pack()
        self._selected_tab = index

    def _show_context_menu(self, a0: QPoint):
        tab_bar = self._tab_widget.tabBar()
        tab_index = -1
        if tab_bar is not None:
            tab_index = tab_bar.tabAt(a0)
        
        R4UIMenuListBuilder() \
            .add_separator() \
            .add_actions([
                R4UIActionMenuItem("Rename", lambda: self._prompt_rename_draft_list_pack(tab_index)),
                R4UIActionMenuItem("Move left", lambda: self._data_source_draft_list.move_pack_left(tab_index)),
                R4UIActionMenuItem("Move right", lambda: self._data_source_draft_list.move_pack_right(tab_index)),
                R4UIActionMenuItem(f"Delete - {self._data_source_draft_list.pack_name(tab_index)}", lambda: self._delete_pack(tab_index)),
            ]) \
            .exec_menu(self._tab_widget.mapToGlobal(a0))
    
    def _prompt_rename_draft_list_pack(self, pack_index: int):
        pack_name, ok = self._router.prompt_text_input('Rename', 'Enter pack name:')
        if ok:
            self._data_source_draft_list.update_pack_name(pack_index, pack_name)
    
    def _delete_pack(self, pack_index: int):
        if self._router.prompt_accept("Delete Pack?", f"Are you sure you want to delete {self._data_source_draft_list.pack_name(pack_index)}"):
            self._data_source_draft_list.remove_pack(pack_index)
    
    def _clear_tabs(self):
        while self._tab_widget.count() > 0:
            # properly clear tabs to remove references from observation tower
            widget_to_delete = self._tab_widget.widget(0) # Get the widget of the first tab
            self._tab_widget.removeTab(0) # Remove the tab
            if widget_to_delete is not None:
                widget_to_delete.deleteLater() # Schedule deletion of the widget
                
    def _sync_draft_list(self):
        self._clear_tabs()
        for pack in self._data_source_draft_list.draft_packs:
            
            view_controller = DraftListTablePackPreviewViewController(self._app_dependencies_provider, 
                                                                  self._data_source_local_resource_provider)
            delegate = DraftListTabbedPackPreviewViewControllerDraftListTablePackPreviewViewControllerDelegate(pack.pack_identifier)
            view_controller.delegate = delegate
            self._tab_widget.addTab(view_controller, pack.pack_name)
        self._tab_widget.addTab(RWidget(), "+")
        if self._selected_tab >= len(self._data_source_draft_list.pack_names):
            self._tab_widget.setCurrentIndex(self._selected_tab - 1)
        else:
            self._tab_widget.setCurrentIndex(self._selected_tab)
    
    def _sync_button(self):
        add_card_mode = self._configuration.draft_list_add_card_mode
        destination_string = self._configuration.draft_list_add_card_deployment_destination
        # TODO: move to view model?
        if add_card_mode == Configuration.Settings.DraftListAddCardMode.OFF or destination_string is None:
            self._add_card_button.setText("Add Card (Ctrl+D)")
            self._add_card_button.setEnabled(True)
        elif add_card_mode == Configuration.Settings.DraftListAddCardMode.STAGE:
            self._add_card_button.setText(f"Add Card and Stage (Ctrl+D)")
            self._add_card_button.setEnabled(True)
        elif add_card_mode == Configuration.Settings.DraftListAddCardMode.STAGE_AND_PUBLISH:
            self._add_card_button.setText(f"Add Card and Publish (Ctrl+D)")
            selected_resource = self._data_source_local_resource_provider.data_source.selected_local_resource
            self._add_card_button.setEnabled(selected_resource is not None and selected_resource.is_ready and self._is_publishing == False)
    
    def _sync_ui(self):
        self._sync_draft_list()
        self._sync_button()
        
    # MARK: - TransmissionReceiverProtocol
    
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == LocalCardResourceFetchEvent or type(event) == LocalCardResourceSelectedFromDataSourceEvent:
            if event.local_resource == self._data_source_local_resource_provider.data_source.selected_local_resource:
                self._sync_button()
        if type(event) == DraftPackUpdatedEvent or \
            type(event) == ConfigurationUpdatedEvent:
            self._sync_ui()
        if type(event) == PublishStagedCardResourcesEvent:
            if event.event_type == PublishStagedCardResourcesEvent.EventType.STARTED:
                self._is_publishing = True
            else:
                self._is_publishing = False
            # print(self._is_publishing)
            self._sync_ui()
        if type(event) == ProductionCardResourcesLoadEvent:
            self._reset_deployment_destination_selection()