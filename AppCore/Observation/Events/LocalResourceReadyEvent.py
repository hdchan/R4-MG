from ...Models.LocalCardResource import LocalCardResource
from ..TransmissionProtocol import TransmissionProtocol
class LocalResourceReadyEvent(TransmissionProtocol):
    def __init__(self, local_resource: LocalCardResource):
        self.local_resource = local_resource