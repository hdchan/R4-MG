from enum import Enum
from typing import Optional, Type
from .WebSocketMessageProtocol import WebSocketMessageProtocol
from typing import Protocol, runtime_checkable

@runtime_checkable
class WebSocketMessageReceiverProtocol(Protocol):
    def wsmr_handle_websocket_message(self, message: WebSocketMessageProtocol) -> None:
        raise Exception()

class WebSocketClientObjectProtocol:
    def wbc_send_message(self, message: WebSocketMessageProtocol):
        raise Exception()



class WebSocketHostObjectProtocol:
    def wsh_handle_new_connection(self, client_object: WebSocketClientObjectProtocol) -> None:
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
    def ip_address(self) -> Optional[str]:
        raise Exception

    def register_for_messages(self, subscriber: WebSocketMessageReceiverProtocol, event_type: Type[WebSocketMessageProtocol]):
        raise Exception

    def register_as_host(self, host_object: WebSocketHostObjectProtocol):
        raise Exception

    # def register_as_client(self, client_object: WebSocketClientObjectProtocol):
    #     raise Exception

    def send_websocket_message(self, message: WebSocketMessageProtocol):
        raise Exception