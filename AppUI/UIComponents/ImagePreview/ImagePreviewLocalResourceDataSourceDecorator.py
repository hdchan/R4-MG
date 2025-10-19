from typing import Optional
import copy
from AppCore.Models import (DataSourceSelectedLocalCardResourceProtocol,
                          LocalResourceDataSourceProviding)
from AppCore.Models import LocalCardResource
from AppCore.Observation import *
from AppCore.Observation.Events import LocalCardResourceSelectedFromDataSourceEvent

from .ImagePreviewViewController import ImagePreviewViewController


class ImagePreviewLocalResourceDataSourceDecorator(ImagePreviewViewController, LocalResourceDataSourceProviding, DataSourceSelectedLocalCardResourceProtocol):
    
    def set_image(self, local_resource: LocalCardResource):
        super().set_image(local_resource)
        self._observation_tower.notify(LocalCardResourceSelectedFromDataSourceEvent(copy.deepcopy(local_resource), self))
        
    
    # MARK: - LocalResourceDataSourceProviding, DataSourceSelectedLocalCardResourceProtocol
    @property
    def data_source(self) -> DataSourceSelectedLocalCardResourceProtocol:
        return self
    
    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        return self._local_resource