import weakref
from typing import Dict, List, Type
from weakref import ReferenceType

from .TransmissionProtocol import TransmissionProtocol
from .TransmissionReceiver import TransmissionReceiver


class ObservationTower:

    def __init__(self):
         self.subscribers: Dict[Type[TransmissionProtocol], List[ReferenceType[TransmissionReceiver]]] = {}

    def notify(self, event: TransmissionProtocol):
        # filter dead subscribers
        if event.__class__ not in self.subscribers:
            return
        filtered_subscribers = filter(lambda x: x() is not None, self.subscribers[event.__class__])
        self.subscribers[event.__class__] = list(filtered_subscribers)
        if event.__class__ in self.subscribers:
            for s in self.subscribers[event.__class__]:
                 s().handle_observation_tower_event(event) # type: ignore

    def subscribe(self, subscriber: TransmissionReceiver, eventType: Type[TransmissionProtocol]):
        if eventType not in self.subscribers:
            self.subscribers[eventType] = []
        self.subscribers[eventType].append(weakref.ref(subscriber))