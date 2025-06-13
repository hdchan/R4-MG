from AppCore.Models.LocalCardResource import LocalCardResource

from ..TransmissionProtocol import TransmissionProtocol


class LocalResourceSelectedEvent(TransmissionProtocol):
    def __init__(self,
                 local_resource: LocalCardResource):
        self.local_resource = local_resource