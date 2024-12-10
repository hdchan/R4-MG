from enum import Enum
from typing import List

from ...Models import StagedCardResource
from ..TransmissionProtocol import TransmissionProtocol


class PublishStagedResourcesEvent(TransmissionProtocol):
    class EventType(Enum):
        STARTED = 0
        FINISHED = 1
        FAILED = 2

    def __init__(self, event_type: EventType, published_resources: List[StagedCardResource]):
        super().__init__()
        self.event_type = event_type
        self.published_resources = published_resources