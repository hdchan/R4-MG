from AppCore.Models import LocalResourceDraftListWindow

from ..TransmissionProtocol import TransmissionProtocol


class DraftListWindowResourceUpdatedEvent(TransmissionProtocol):
        
    def __init__(self, 
                 new_resource: LocalResourceDraftListWindow,
                 old_resource: LocalResourceDraftListWindow):
        self.old_resource = old_resource
        self.new_resource = new_resource