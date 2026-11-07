from typing import List, Optional

from AppCore.Models import LocalResourceDraftListWindow

class DataSourceDraftListWindowResourceDeployerProtocol:
    @property
    def draft_list_windows(self) -> List[LocalResourceDraftListWindow]:
        raise Exception

    def load_resources(self):
        raise Exception

    def create_new_window(self, window_name: str):
        raise Exception

    def delete_window_resource(self, resource: LocalResourceDraftListWindow):
        raise Exception

    def unbind_draft_pack_name(self, resource: LocalResourceDraftListWindow):
        raise Exception

    def update_window_dimension(self, resource: LocalResourceDraftListWindow, width: Optional[int], height: Optional[int]):
        raise Exception

    def update_window_draft_pack(self, resource: LocalResourceDraftListWindow, draft_pack_identifier: Optional[str]):
        raise Exception

class DataSourceDraftListWindowResourceDeployerProviding:
    @property
    def draft_list_window_resource_data_source(self) -> DataSourceDraftListWindowResourceDeployerProtocol:
        raise Exception