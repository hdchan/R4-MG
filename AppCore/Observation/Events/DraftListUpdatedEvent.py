from ..TransmissionProtocol import TransmissionProtocol
from AppCore.Models import DraftPack, LocalCardResource
class DraftListUpdatedEvent(TransmissionProtocol):
    
    class EventType:
        pass
    
    class AddedResource(EventType):
        def __init__(self, index: int, local_resource: LocalCardResource):
            self.index = index
            self.local_resource = local_resource
            pass
        
    class SwappedResources(EventType):
        def __init__(self, index_1: int, index_2: int):
            self.index_1 = index_1
            self.index_2 = index_2
            
    class RemovedResource(EventType):
        def __init__(self, index: int):
            self.index = index
            
    class InsertedResource(EventType):
        def __init__(self, index: int, local_resource: LocalCardResource):
            self.index = index
            self.local_resource = local_resource
    
    def __init__(self, draft_pack: DraftPack, event_type: EventType):
        super().__init__()
        self.draft_pack = draft_pack
        self.event_type = event_type