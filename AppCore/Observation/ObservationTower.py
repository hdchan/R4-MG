import weakref
from typing import Dict, List, Type, Callable, Optional
from weakref import ReferenceType

from .TransmissionProtocol import TransmissionProtocol
from .TransmissionReceiverProtocol import TransmissionReceiverProtocol

TransmissionReceiverHandlerCallback = Callable[TransmissionProtocol, None]

class ObservationTower:

    def __init__(self):
         self._is_debug = False
         self._subscribers: Dict[Type[TransmissionProtocol], List[ReferenceType[TransmissionReceiverProtocol]]] = {}
         self._subscriber_handlers: Dict[str, List[ReferenceType[TransmissionReceiverHandlerCallback]]] = {}

    def set_debug(self, is_debug: bool):
        self._is_debug = is_debug

    @property
    def subscribers(self) -> Dict[Type[TransmissionProtocol], List[ReferenceType[TransmissionReceiverProtocol]]]:
        return self._subscribers

    def notify(self, event: TransmissionProtocol):
        # Updated events
        key = f'{event.__class__.__name__}'
        if event.transmission_identifier is not None:
            key = f'{key}.{event.transmission_identifier}'
        if key in self._subscriber_handlers:
            for h in self._subscriber_handlers[key][:]:
                if h() is None:
                    self._subscriber_handlers[key].remove(h)
            for h in self._subscriber_handlers[key]:
                if h() is None:
                    continue
                try:
                    h()(event)
                except Exception as e:
                    print(e)

        # Normal events
        if event.__class__ not in self._subscribers:
            return
        
        dead_subscribers: Dict[Type[TransmissionProtocol], List[ReferenceType[TransmissionReceiverProtocol]]] = {}
        for key in self._subscribers:
            dead_subscribers[key] = []
            for s in self._subscribers[key]:
                if s() is None:
                    dead_subscribers[key].append(s)
        for key in dead_subscribers:
            for s in dead_subscribers[key]:
                self._subscribers[key].remove(s)
        
        if event.__class__ in self._subscribers:
            event_subscribers = self._subscribers[event.__class__]
            for s in event_subscribers:
                try:
                    s().handle_observation_tower_event(event) # type: ignore
                except Exception as e:
                    print(str(e))
        if self._is_debug:
            self._debug_log(event)

    def subscribe_handler(self, handler: TransmissionReceiverHandlerCallback, event_type: Type[TransmissionProtocol], transmission_identifier: Optional[str] = None):
        key = f'{event_type.__name__}'
        if transmission_identifier is not None:
            key = f'{key}.{transmission_identifier}'
        if key not in self._subscriber_handlers:
            self._subscriber_handlers[key] = []
        self._subscriber_handlers[key].append(weakref.WeakMethod(handler))

    def unsubscribe_handler(self, handler: TransmissionReceiverHandlerCallback, event_type: Type[TransmissionProtocol], transmission_identifier: Optional[str] = None):
        key = f'{event_type.__name__}'
        if transmission_identifier is not None:
            key = f'{key}.{transmission_identifier}'
        if key not in self._subscriber_handlers:
            return
        for h in self._subscriber_handlers[key]:
            # print(h)
            try:
                if h() == handler:
                    self._subscriber_handlers[key].remove(h)
            except Exception as e:
                print(str(e))
        pass

    def subscribe(self, subscriber: TransmissionReceiverProtocol, event_type: Type[TransmissionProtocol]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(weakref.ref(subscriber))
        
    def subscribe_multi(self, subscriber: TransmissionReceiverProtocol, event_types: List[Type[TransmissionProtocol]]):
        for e in event_types:
            self.subscribe(subscriber, e)
            
    def _debug_log(self, current_event: TransmissionProtocol):
        subscribers = self.subscribers
        result: Dict[Type[TransmissionProtocol], int] = {}
        for key in subscribers.keys():
            result[key] = len(subscribers[key])
        res =  max(result, key=result.get)
        text = f'{current_event.__class__} {res} {result[res]})'
        print(text)