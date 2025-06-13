from enum import Enum

from AppCore.Models import DeploymentCardResource

from ..TransmissionProtocol import TransmissionProtocol


class DeploymentResourceEvent(TransmissionProtocol):
    class EventType(int, Enum):
        STAGED = 0
        CLEARED = 1
        
    def __init__(self, deployment_resource: DeploymentCardResource, event_type: EventType):
        self.deployment_resource = deployment_resource
        self.event_type = event_type