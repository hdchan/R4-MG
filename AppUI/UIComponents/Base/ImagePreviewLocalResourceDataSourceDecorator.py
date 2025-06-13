from typing import Optional

from AppCore.Data import (LocalResourceDataSourceProtocol,
                          LocalResourceDataSourceProviding)
from AppCore.Models import LocalCardResource
from AppCore.Observation import *
from AppCore.Observation.Events import LocalResourceSelectedEvent

from .ImagePreviewViewController import ImagePreviewViewController


class ImagePreviewLocalResourceDataSourceDecorator(ImagePreviewViewController, LocalResourceDataSourceProviding, LocalResourceDataSourceProtocol):
    
    def set_image(self, local_resource: LocalCardResource):
        super().set_image(local_resource)
        self._observation_tower.notify(LocalResourceSelectedEvent(local_resource)) # rework?
        
    
    # MARK: - LocalResourceDataSourceProviding, LocalResourceDataSourceProtocol
    @property
    def data_source(self) -> LocalResourceDataSourceProtocol:
        return self
    
    @property
    def selected_local_resource(self) -> Optional[LocalCardResource]:
        return self._local_resource