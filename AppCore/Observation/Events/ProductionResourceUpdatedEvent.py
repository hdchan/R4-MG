from ...Models.LocalCardResource import LocalCardResource
from ..TransmissionProtocol import TransmissionProtocol


class ProductionResourceUpdatedEvent(TransmissionProtocol):
    def __init__(self, local_resource: LocalCardResource):
        self.local_resource = local_resource