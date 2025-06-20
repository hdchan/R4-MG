from enum import Enum
from typing import List

from AppCore.Models.DeploymentCardResource import DeploymentCardResource
from ..TransmissionProtocol import TransmissionProtocol


class PublishStagedCardResourcesEvent(TransmissionProtocol):
    class EventType(int, Enum):
        STARTED = 0
        FINISHED = 1
        FAILED = 2

    def __init__(self, event_type: EventType, deployment_resources: List[DeploymentCardResource]):
        super().__init__()
        self.event_type = event_type
        self.deployment_resources = deployment_resources