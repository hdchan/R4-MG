from ..DataSourceDraftListProtocol import DataSourceDraftListProtocol
from typing import List, Any
from AppCore.Models import LocalCardResource


class DataSourceDraftListWebSocketMessagePartials:
    @staticmethod
    def clear_entire_draft_list(data_source: DataSourceDraftListProtocol):
        data_source.clear_entire_draft_list()

    @staticmethod
    def keep_packs_clear_lists(data_source: DataSourceDraftListProtocol):
        data_source.keep_packs_clear_lists()

    @staticmethod
    def create_new_pack(data_source: DataSourceDraftListProtocol):
        data_source.create_new_pack()

    @staticmethod
    def create_new_pack_from_list(name: str,
                                  list: List[LocalCardResource],
                                  data_source: DataSourceDraftListProtocol):
        data_source.create_new_pack_from_list(name, list)

    @staticmethod
    def update_pack_name(pack_index: int,
                         name: str,
                         data_source: DataSourceDraftListProtocol):
        data_source.update_pack_name(pack_index, name)

    @staticmethod
    def remove_pack(pack_index: int,
                    data_source: DataSourceDraftListProtocol):
        data_source.remove_pack(pack_index)

    @staticmethod
    def swap_pack_positions(pi1: int,
                            pi2: int,
                            data_source: DataSourceDraftListProtocol):
        data_source.swap_pack_positions(pi1, pi2)

    # MARK: - modify resource order
    @staticmethod
    def add_resource_to_pack(pack_index: int,
                             local_resource: LocalCardResource,
                             data_source: DataSourceDraftListProtocol):
        data_source.add_resource_to_pack(pack_index, local_resource)

    @staticmethod
    def remove_resource(pack_index: int,
                        resource_index: int,
                        data_source: DataSourceDraftListProtocol):
        data_source.remove_resource(pack_index, resource_index)

    @staticmethod
    def swap_resources(pack_index: int,
                       ri1: int,
                       ri2: int,
                       data_source: DataSourceDraftListProtocol):
        data_source.swap_resources(pack_index, ri1, ri2)

    @staticmethod
    def insert_resource(pack_index: int,
                        resource_index: int,
                        local_resource: LocalCardResource,
                        data_source: DataSourceDraftListProtocol):
        data_source.insert_resource(pack_index, resource_index, local_resource)

    @staticmethod
    def mark_resource_as_sideboard(pack_index: int,
                                   resource_index: int,
                                   key: str, 
                                   value: Any,
                                   data_source: DataSourceDraftListProtocol):
        data_source.mark_resource_as_sideboard(pack_index, resource_index, key, value)
