from typing import Optional

from ..Observation.ObservationTower import *
from .LocalCardResource import *

class DeploymentCardResource:
    def __init__(self, production_resource: LocalCardResource):
        self.production_resource = production_resource
        self.staged_resource: Optional[LocalCardResource] = None

    def stage(self, local_resource: LocalCardResource):
        self.staged_resource = local_resource

    def clear_staged_resource(self):
        if self.staged_resource is not None:
            self.staged_resource = None
        
    @property
    def can_publish_staged_resource(self) -> bool:
        return self.staged_resource is not None and self.staged_resource.is_ready