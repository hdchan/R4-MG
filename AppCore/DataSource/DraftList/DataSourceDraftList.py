import copy
from typing import Any, List

from AppCore.Config import ConfigurationManager
from AppCore.Models import DraftPack, LocalCardResource
from AppCore.Observation import ObservationTower
from AppCore.Service.DataSerializer import DataSerializer

from .DataSourceDraftListProtocol import DataSourceDraftListProtocol
from .Events import DraftListUpdatedEvent, DraftPackUpdatedEvent
from AppCore.DataSource.ImageResourceDeployer.DataSourceImageResourceDeployerProtocol import DataSourceImageResourceDeployerProviding, DataSourceImageResourceDeployerProtocol
from AppCore.Config import Configuration

class DataSourceDraftList(DataSourceDraftListProtocol):

    def __init__(self,
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower,
                 data_serializer: DataSerializer, 
                 data_source_image_resource_deployer_provider: DataSourceImageResourceDeployerProviding):
        self._configuration_manager = configuration_manager
        self._observation_tower = observation_tower
        self._data_serializer = data_serializer
        self._data_source_image_resource_deployer_provider = data_source_image_resource_deployer_provider

        self._packs: List[DraftPack] = []

        self._file_path = f'{self._configuration_manager.configuration.draft_lists_dir_path}draft_list.json'
        loaded = self._data_serializer.load(self._file_path)
        if loaded is not None:
            for pack_json in loaded:
                self._packs.append(DraftPack.from_json(pack_json))

    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration

    @property
    def _data_source_image_resource_deployer(self) -> DataSourceImageResourceDeployerProtocol:
        return self._data_source_image_resource_deployer_provider.data_source_image_resource_deployer

    @property
    def draft_packs(self) -> List[DraftPack]:
        return self._packs

    # MARK: - modify packs
    def clear_entire_draft_list(self):
        self._packs = []
        self._save_and_notify_draft_pack_update()
        self.create_new_pack()

    def keep_packs_clear_lists(self):
        for p in self._packs:
            p.clear_draft_list()
        self._save_and_notify_draft_pack_update()

    def create_new_pack(self):
        starting_counter = len(self._packs) + 1
        name = f"New Pack {starting_counter}"
        while True:
            name = f"New Pack {starting_counter}"
            if name not in self.pack_names:
                break
            starting_counter += 1
        new_pack = DraftPack.new_draft_pack(name)
        self._packs.append(new_pack)
        self._save_and_notify_draft_pack_update()

    def create_new_pack_from_list(self, name: str, list: List[LocalCardResource]):
        new_pack = DraftPack.new_draft_pack(name)
        new_pack.add_resources(list)
        self._packs.append(new_pack)
        self._save_and_notify_draft_pack_update()

    def update_pack_name(self, pack_index: int, name: str):
        if pack_index >= 0 and pack_index < len(self._packs):
            pack = self._packs[pack_index]
            pack.update_pack_name(name)
            self._save_and_notify_draft_pack_update()

    def remove_pack(self, pack_index: int):
        if pack_index >= 0 and pack_index < len(self._packs):
            del self._packs[pack_index]

            if len(self._packs) == 0:
                self.create_new_pack()

            self._save_and_notify_draft_pack_update()

    def move_pack_left(self, pack_index: int):
        if pack_index >= 0 and pack_index < len(self._packs):
            self.swap_pack_positions(pack_index, pack_index - 1)

    def move_pack_right(self, pack_index: int):
        if pack_index >= 0 and pack_index < len(self._packs):
            self.swap_pack_positions(pack_index, pack_index + 1)

    def swap_pack_positions(self, pi1: int, pi2: int):
        if pi1 >= 0 and pi1 < len(self._packs) and pi2 >= 0 and pi2 < len(self._packs):
            self._packs[pi1], self._packs[pi2] = self._packs[pi2], self._packs[pi1]
            self._save_and_notify_draft_pack_update()

    # MARK: - modify resource order
    def add_resource_to_pack(self, pack_index: int, local_resource: LocalCardResource):
        if local_resource.trading_card is None:
            raise Exception("No underlying trading card. Use another.")
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].add_resource(local_resource)

            self._stage_publish_draft_item_if_needed(local_resource)

            event_type = DraftListUpdatedEvent.AddedResource(pack_index=pack_index,
                                                             index=len(
                                                                 self._packs) - 1,
                                                             local_resource=local_resource)
            self._save_and_notify_draft_list_update(
                self._packs[pack_index], event_type)

    def _stage_publish_draft_item_if_needed(self, selected_resource: LocalCardResource):
        destination_file_name = self._configuration.draft_list_add_card_deployment_destination
        if destination_file_name is None:
            return
        
        matching_deployment_resource = self._data_source_image_resource_deployer.deployment_resource_for_file_name(destination_file_name)
        
        if matching_deployment_resource is None:
            # self._reset_deployment_destination_selection() # TODO: do we need to reimplement this somehow
            return
        add_card_mode = self._configuration.draft_list_add_card_mode
        
        if add_card_mode == Configuration.Settings.DraftListAddCardMode.STAGE or add_card_mode == Configuration.Settings.DraftListAddCardMode.STAGE_AND_PUBLISH:
            self._data_source_image_resource_deployer.stage_resource(matching_deployment_resource, selected_resource)
        if add_card_mode == Configuration.Settings.DraftListAddCardMode.STAGE_AND_PUBLISH:
            self._data_source_image_resource_deployer.publish_staged_resources()

    def remove_resource(self, pack_index: int, resource_index: int):
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].remove_resource(resource_index)
            event_type = DraftListUpdatedEvent.RemovedResource(pack_index=pack_index,
                                                               index=resource_index)
            self._save_and_notify_draft_list_update(
                self._packs[pack_index], event_type)

    def swap_resources(self, pack_index: int, ri1: int, ri2: int):
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].swap_resources(ri1, ri2)
            event_type = DraftListUpdatedEvent.SwappedResources(pack_index=pack_index,
                                                                index_1=ri1,
                                                                index_2=ri2)
            self._save_and_notify_draft_list_update(self._packs[pack_index], event_type)

    def insert_resource(self, pack_index: int, resource_index: int, local_resource: LocalCardResource):
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].insert_resource(resource_index, local_resource)
            event_type = DraftListUpdatedEvent.InsertedResource(pack_index=pack_index,
                                                                index=resource_index,
                                                                local_resource=local_resource)
            self._save_and_notify_draft_list_update(self._packs[pack_index], event_type)

    def mark_resource_as_sideboard(self, pack_index: int, resource_index: int, key: str, value: Any):
        if pack_index >= 0 and pack_index < len(self._packs):
            self._packs[pack_index].mark_resource_as_sideboard(
                resource_index, key, value)
            event_type = DraftListUpdatedEvent.UpdateResource(pack_index=pack_index,
                                                              index=resource_index)
            self._save_and_notify_draft_list_update(
                self._packs[pack_index], event_type)

    def _save_and_notify_draft_pack_update(self):
        self._data_serializer.save_json_data(self._file_path, self._packs)
        self._observation_tower.notify(DraftPackUpdatedEvent())

    def _save_and_notify_draft_list_update(self, draft_pack: DraftPack, event_type: DraftListUpdatedEvent.GeneralEventType):
        self._data_serializer.save_json_data(self._file_path, self._packs)
        self._observation_tower.notify(DraftListUpdatedEvent(event_type))
