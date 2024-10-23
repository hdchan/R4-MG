from ...Models.LocalCardResource import LocalCardResource
from ..TransmissionProtocol import TransmissionProtocol
from typing import List

class ProductionResourcesLoadedEvent(TransmissionProtocol):
    def __init__(self, production_resources: List[LocalCardResource]):
        self.production_resources = production_resources