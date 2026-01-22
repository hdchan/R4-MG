import weakref
from typing import Dict, List
from weakref import ReferenceType

from .WebSocketMessageProtocol import WebSocketMessageProtocol
from .WebSocketServiceProtocol import WebSocketMessageReceiverProtocol


class WebSocketMessenger:
    def __init__(self):
        self._subscribers: Dict[str,
                                ReferenceType[WebSocketMessageReceiverProtocol]] = {}

    def register_for_messages(self, identifier: str, subscriber: WebSocketMessageReceiverProtocol):
        # if self._subscribers[identifier] is not None:
        #     raise Exception("only one receiver of messages is allowed")
        self._subscribers[identifier] = weakref.ref(subscriber)

    def deliver_message(self, message: WebSocketMessageProtocol):
        if message.identifier in self._subscribers:
            s = self._subscribers[message.identifier]
            s().handle_websocket_message(message)
