from AppCore.Observation.TransmissionProtocol import TransmissionProtocol
from AppCore.Models import LocalCardResource
class DraftListUpdatedEvent(TransmissionProtocol):
    
    class GeneralEventType:
        pass
    
    class AddedResource(GeneralEventType):
        def __init__(self, pack_index: int, index: int, local_resource: LocalCardResource):
            self.pack_index = pack_index
            self.index = index
            self.local_resource = local_resource
            pass
        
    class SwappedResources(GeneralEventType):
        def __init__(self, pack_index: int, index_1: int, index_2: int):
            self.pack_index = pack_index
            self.index_1 = index_1
            self.index_2 = index_2
            
    class RemovedResource(GeneralEventType):
        def __init__(self, pack_index: int, index: int):
            self.pack_index = pack_index
            self.index = index
            
    class InsertedResource(GeneralEventType):
        def __init__(self, pack_index: int, index: int, local_resource: LocalCardResource):
            self.pack_index = pack_index
            self.index = index
            self.local_resource = local_resource

    class UpdateResource(GeneralEventType):
        # TODO: pass updated card?
        def __init__(self, pack_index: int, index: int):
            self.pack_index = pack_index
            self.index = index
    
    def __init__(self, event_type: GeneralEventType):
        super().__init__()
        self.event_type = event_type