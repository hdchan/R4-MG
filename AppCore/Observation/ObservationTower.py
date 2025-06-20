import weakref
from typing import Dict, List, Type
from weakref import ReferenceType

from .TransmissionProtocol import TransmissionProtocol
from .TransmissionReceiverProtocol import TransmissionReceiverProtocol


class ObservationTower:

    def __init__(self):
         self.subscribers: Dict[Type[TransmissionProtocol], List[ReferenceType[TransmissionReceiverProtocol]]] = {}

    def notify(self, event: TransmissionProtocol):
        if event.__class__ not in self.subscribers:
            return
        dead_subscribers: List[ReferenceType[TransmissionReceiverProtocol]] = []
        if event.__class__ in self.subscribers:
            for s in self.subscribers[event.__class__]:
                try:
                    s().handle_observation_tower_event(event) # type: ignore
                except:
                    dead_subscribers.append(s)
        # filter dead subscribers
        for s in dead_subscribers:
            self.subscribers[event.__class__].remove(s)

    def subscribe(self, subscriber: TransmissionReceiverProtocol, eventType: Type[TransmissionProtocol]):
        if eventType not in self.subscribers:
            self.subscribers[eventType] = []
        self.subscribers[eventType].append(weakref.ref(subscriber))
        
    def subscribe_multi(self, subscriber: TransmissionReceiverProtocol, eventTypes: List[Type[TransmissionProtocol]]):
        for e in eventTypes:
            self.subscribe(subscriber, e)