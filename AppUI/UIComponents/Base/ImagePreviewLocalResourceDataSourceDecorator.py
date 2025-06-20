from typing import Optional

from AppCore.DataSource import (DataSourceSelectedLocalCardResourceProtocol,
                          LocalResourceDataSourceProviding)
from AppCore.Models import LocalCardResource
from AppCore.Observation import *
from AppCore.Observation.Events import LocalCardResourceSelectedEvent

from .ImagePreviewViewController import ImagePreviewViewController


class ImagePreviewLocalResourceDataSourceDecorator(ImagePreviewViewController, LocalResourceDataSourceProviding, DataSourceSelectedLocalCardResourceProtocol):
    
    def set_image(self, local_resource: LocalCardResource):
        super().set_image(local_resource)
        self._observation_tower.notify(LocalCardResourceSelectedEvent(local_resource)) # rework?
        
    
    # MARK: - LocalResourceDataSourceProviding, DataSourceSelectedLocalCardResourceProtocol
    @property
    def data_source(self) -> DataSourceSelectedLocalCardResourceProtocol:
        return self
    
    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        return self._local_resource