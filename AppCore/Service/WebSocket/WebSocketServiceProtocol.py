from enum import Enum
from typing import Optional
from .WebSocketMessageProtocol import WebSocketMessageProtocol
from typing import Protocol, runtime_checkable

@runtime_checkable
class WebSocketMessageReceiverProtocol(Protocol):
    def handle_websocket_message(self, message: WebSocketMessageProtocol) -> None:
        raise Exception()

class WebSocketClientObjectProtocol:
    def send_message(self, message: WebSocketMessageProtocol):
        raise Exception()

class WebSocketHostObjectProtocol:
    def handle_new_connection(self) -> WebSocketMessageProtocol:
        raise Exception()

class WebSocketServiceStatus(int, Enum):
    NONE = 0
    IS_HOST = 1
    IS_CLIENT = 2
    ERROR = 3

@runtime_checkable
class WebSocketServiceProtocol(Protocol):
    def connect_as_host(self) -> None:
        raise Exception

    def connect_as_client(self, ip: str, port: Optional[int]) -> None:
        raise Exception

    def disconnect(self) -> None:
        raise Exception

    @property
    def state(self) -> WebSocketServiceStatus:
        raise Exception

    @property
    def ip_address(self) -> str:
        raise Exception

    def register_for_messages(self, identifier: str, subscriber: WebSocketMessageReceiverProtocol):
        raise Exception

    def register_as_host(self, host_object: WebSocketHostObjectProtocol):
        raise Exception

    def send_message(self, message: WebSocketMessageProtocol):
        raise Exception

class WebSocketHostDelegate:
    def host_started(self, is_started: bool) -> None:
        return

    def host_stopped(self) -> None:
        return

    def host_received_message(self, message: str) -> None:
        return

class WebSocketClientDelegate:
    def client_connected(self) -> None:
        return

    def client_disconnected(self) -> None:
        return

    def client_received_message(self, message: str) -> None:
        return