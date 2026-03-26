import weakref
from typing import Dict, Type
from weakref import ReferenceType

from .WebSocketMessageProtocol import WebSocketMessageProtocol
from .WebSocketServiceProtocol import WebSocketMessageReceiverProtocol


class WebSocketMessenger:
    def __init__(self):
        self._subscribers: Dict[Type[WebSocketMessageProtocol],
                                ReferenceType[WebSocketMessageReceiverProtocol]] = {}

    def register_for_messages(self, subscriber: WebSocketMessageReceiverProtocol, event_type: Type[WebSocketMessageProtocol]):
        self._subscribers[event_type] = weakref.ref(subscriber)

    def deliver_message(self, message: WebSocketMessageProtocol):
        if message.__class__ in self._subscribers:
            s = self._subscribers[message.__class__]
            try:
                s().wsmr_handle_websocket_message(message) # type: ignore
            except Exception as e:
                print(str(e))
