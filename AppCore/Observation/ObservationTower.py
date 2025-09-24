import copy
import weakref
from typing import Dict, List, Type
from weakref import ReferenceType

from .TransmissionProtocol import TransmissionProtocol
from .TransmissionReceiverProtocol import TransmissionReceiverProtocol


class ObservationTower:

    def __init__(self):
         self._subscribers: Dict[Type[TransmissionProtocol], List[ReferenceType[TransmissionReceiverProtocol]]] = {}

    @property
    def subscribers(self) -> Dict[Type[TransmissionProtocol], List[ReferenceType[TransmissionReceiverProtocol]]]:
        return copy.deepcopy(self._subscribers)

    def notify(self, event: TransmissionProtocol):
        if event.__class__ not in self._subscribers:
            return
        
        dead_subscribers: Dict[Type[TransmissionProtocol], List[ReferenceType[TransmissionReceiverProtocol]]] = {}
        for key in self._subscribers:
            dead_subscribers[key] = []
            for s in self._subscribers[key]:
                if s() == None:
                    dead_subscribers[key].append(s)
        for key in dead_subscribers:
            for s in dead_subscribers[key]:
                self._subscribers[key].remove(s)
        
        if event.__class__ in self._subscribers:
            event_subscribers = self._subscribers[event.__class__]
            for s in event_subscribers:
                try:
                    s().handle_observation_tower_event(event) # type: ignore
                except:
                    pass
                
        self._debug_log(event)

    def subscribe(self, subscriber: TransmissionReceiverProtocol, eventType: Type[TransmissionProtocol]):
        if eventType not in self._subscribers:
            self._subscribers[eventType] = []
        self._subscribers[eventType].append(weakref.ref(subscriber))
        
    def subscribe_multi(self, subscriber: TransmissionReceiverProtocol, eventTypes: List[Type[TransmissionProtocol]]):
        for e in eventTypes:
            self.subscribe(subscriber, e)
            
    def _debug_log(self, current_event):
        subscribers = self.subscribers
        result: Dict[Type[TransmissionProtocol], int] = {}
        for key in subscribers.keys():
            result[key] = len(subscribers[key])
        res =  max(result, key=result.get)
        text = f'{current_event.__class__} {res} {result[res]})'
        print(text)