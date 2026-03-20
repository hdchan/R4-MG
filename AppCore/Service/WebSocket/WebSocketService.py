import socket
from typing import List, Optional

import jsonpickle # type: ignore

from AppCore.Observation import ObservationTower
from AppCore.Observation.Events import WebSocketStatusUpdatedEvent

from .WebSocketClient import WebSocketClient
from .WebSocketHost import WebSocketHost
from .WebSocketMessageProtocol import WebSocketMessageProtocol
from .WebSocketMessenger import WebSocketMessenger
from .WebSocketServiceProtocol import (
    WebSocketClientDelegate,
    WebSocketClientObjectProtocol,
    WebSocketHostDelegate,
    WebSocketHostObjectProtocol,
    WebSocketMessageReceiverProtocol,
    WebSocketServiceProtocol,
    WebSocketServiceStatus,
)


class WebSocketService(WebSocketServiceProtocol, WebSocketClientDelegate, WebSocketHostDelegate):
    def __init__(self, observation_tower: ObservationTower):
        super().__init__()
        self._observation_tower = observation_tower
        self._client = WebSocketClient()
        self._client.delegate = self
        self._host = WebSocketHost()
        self._host.delegate = self
        self._messenger = WebSocketMessenger()
        self.__state: WebSocketServiceStatus = WebSocketServiceStatus.NONE
        self._host_objects: List[WebSocketHostObjectProtocol] = []

    @property
    def state(self) -> WebSocketServiceStatus:
        return self._state

    def register_as_host(self, host_object: WebSocketHostObjectProtocol):
        self._host_objects.append(host_object)

    def register_for_messages(self, identifier: str, subscriber: WebSocketMessageReceiverProtocol):
        self._messenger.register_for_messages(identifier, subscriber)

    @property
    def _state(self) -> WebSocketServiceStatus:
        return self.__state

    @_state.setter
    def _state(self, value: WebSocketServiceStatus):
        if self.__state != value:
            self.__state = value
            self._observation_tower.notify(WebSocketStatusUpdatedEvent())

    def connect_as_host(self) -> None:
        self._host.start_server()

    def connect_as_client(self, ip: str, port: Optional[int]) -> None:
        self._client.connect_to_server(ip, port)

    def disconnect(self) -> None:
        self._client.disconnect()
        self._host.stop_server()

    def send_message(self, message: WebSocketMessageProtocol):
        message_str: str = jsonpickle.encode(message, make_refs=False)
        if self._state == WebSocketServiceStatus.IS_HOST:
            self._host.send_message(message_str)
        elif self._state == WebSocketServiceStatus.IS_CLIENT:
            self._client.send_message(message_str)

    @property
    def ip_address(self) -> str:
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            # Filters out loopback addresses, if necessary, but gethostbyname usually avoids this
            if ip_address.startswith("127."):
                # A more reliable method for the actual network IP (works by connecting to an external server like Google DNS without sending data)
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 80))
                ip_address = s.getsockname()[0]
                s.close()
        except socket.error:
            ip_address = "Could not get IP address"
        return ip_address

    # MARK: - DataSourceDraftListWebSocketHostDecoratorDelegate
    def host_started(self, is_started: bool) -> None:
        self._state = WebSocketServiceStatus.IS_HOST if is_started else WebSocketServiceStatus.ERROR

    def host_stopped(self) -> None:
        self._state = WebSocketServiceStatus.NONE

    def host_received_message(self, message: str) -> None:
        self._messenger.deliver_message(jsonpickle.decode(message))

    def host_received_client_connection(self, client_object: WebSocketClientObjectProtocol):
        for i in self._host_objects:
            message = i.handle_new_connection()
            client_object.send_message(message)

    # MARK: - DataSourceDraftListWebSocketClientDecoratorDelegate
    def client_connected(self) -> None:
        self._state = WebSocketServiceStatus.IS_CLIENT

    def client_disconnected(self) -> None:
        self._state = WebSocketServiceStatus.NONE

    def client_received_message(self, message: str) -> None:
        self._messenger.deliver_message(jsonpickle.decode(message))
