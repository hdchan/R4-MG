import weakref
from typing import Dict, List, Type
from weakref import ReferenceType

from .TransmissionProtocol import TransmissionProtocol
from .TransmissionReceiverProtocol import TransmissionReceiverProtocol


class ObservationTower:

    def __init__(self):
         self.subscribers: Dict[Type[TransmissionProtocol], List[ReferenceType[TransmissionReceiverProtocol]]] = {}

    def notify(self, event: TransmissionProtocol):
        # filter dead subscribers
        if event.__class__ not in self.subscribers:
            return
        filtered_subscribers = filter(lambda x: x() is not None, self.subscribers[event.__class__])
        self.subscribers[event.__class__] = list(filtered_subscribers)
        if event.__class__ in self.subscribers:
            for s in self.subscribers[event.__class__]:
                obj = s()
                if obj is not None: # its possible for objs to get deallocated after filtering
                    obj.handle_observation_tower_event(event) # type: ignore

    def subscribe(self, subscriber: TransmissionReceiverProtocol, eventType: Type[TransmissionProtocol]):
        if eventType not in self.subscribers:
            self.subscribers[eventType] = []
        self.subscribers[eventType].append(weakref.ref(subscriber))
        
    def subscribe_multi(self, subscriber: TransmissionReceiverProtocol, eventTypes: List[Type[TransmissionProtocol]]):
        for e in eventTypes:
            self.subscribe(subscriber, e)