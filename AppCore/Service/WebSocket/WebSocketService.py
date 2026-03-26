import socket
import sys
import zlib
from typing import List, Optional, Type

import jsonpickle  # type: ignore
from PySide6.QtCore import QByteArray

from AppCore.Observation import ObservationTower

from .Events import WebSocketStatusUpdatedEvent
from .WebSocketClient import WebSocketClient, WebSocketClientDelegate
from .WebSocketHost import WebSocketHost, WebSocketHostDelegate
from .WebSocketMessageProtocol import WebSocketMessageProtocol
from .WebSocketMessenger import WebSocketMessenger
from .WebSocketServiceProtocol import (
    WebSocketClientObjectProtocol,
    WebSocketHostObjectProtocol,
    WebSocketMessageReceiverProtocol,
    WebSocketServiceProtocol,
    WebSocketServiceStatus,
)
from AppCore.Service.GeneralWorker import AsyncWorker

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
        self._client_objects: List[WebSocketClientObjectProtocol] = []
        self._async_worker = AsyncWorker()

    @property
    def state(self) -> WebSocketServiceStatus:
        return self._state

    def register_as_host(self, host_object: WebSocketHostObjectProtocol):
        self._host_objects.append(host_object)


    def register_for_messages(self, subscriber: WebSocketMessageReceiverProtocol, event_type: Type[WebSocketMessageProtocol]):
        self._messenger.register_for_messages(subscriber, event_type)

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
        self._client.stop_client()
        self._host.stop_server()

    def send_websocket_message(self, message: WebSocketMessageProtocol):
        if self._state == WebSocketServiceStatus.IS_HOST and not self._host.has_clients or self._state == WebSocketServiceStatus.NONE:
            # no need to send out messages for host when there are no clients
            # or when we're not any status
            return

        def _runnable_fn():
            try:
                message_str: str = jsonpickle.encode(message, make_refs=False)
                raw_mem_size = sys.getsizeof(message_str)

                compressed_data = zlib.compress(message_str.encode('utf-8'))
                compressed_mem_size = sys.getsizeof(compressed_data)

                raw_bytes_len = len(message_str.encode('utf-8'))
                compressed_bytes_len = len(compressed_data)

                ratio = compressed_mem_size / raw_mem_size
                reduction = 1 - ratio

                print(f"Original Object Memory: {raw_mem_size} bytes")
                print(f"Compressed Object Memory: {compressed_mem_size} bytes")
                print(f"Raw Data Size: {raw_bytes_len} bytes")
                print(f"Compressed Data Size: {compressed_bytes_len} bytes")
                print(f"Compressed size is {ratio:.2%} of the original.")
                print(f"Total memory reduction: {reduction:.2%}")
                return compressed_data
            except Exception as e:
                print(e)
        
        def _finished(compressed_data):
            if self._state == WebSocketServiceStatus.IS_HOST:
                self._host.send_binary_message(compressed_data)
            elif self._state == WebSocketServiceStatus.IS_CLIENT:
                self._client.send_binary_message(compressed_data)

        self._async_worker.run(_runnable_fn, _finished)

    @property
    def ip_address(self) -> Optional[str]:
        if self._state == WebSocketServiceStatus.IS_HOST:
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
        return self._client.latest_ip

    # MARK: - DataSourceDraftListWebSocketHostDecoratorDelegate
    def host_started(self, is_started: bool) -> None:
        self._state = WebSocketServiceStatus.IS_HOST if is_started else WebSocketServiceStatus.ERROR

    def host_stopped(self) -> None:
        self._state = WebSocketServiceStatus.NONE

    def host_received_message(self, message: str) -> None:
        self._messenger.deliver_message(jsonpickle.decode(message))

    def host_received_binary_message(self, message: QByteArray) -> None:
        decompressed_data = zlib.decompress(message)
        self.host_received_message(decompressed_data.decode('utf-8'))

    def host_received_client_connection(self, client_object: WebSocketClientObjectProtocol) -> None:
        for i in self._host_objects:
            i.wsh_handle_new_connection(client_object)

    # MARK: - DataSourceDraftListWebSocketClientDecoratorDelegate
    def client_connected(self) -> None:
        self._state = WebSocketServiceStatus.IS_CLIENT

    def client_disconnected(self) -> None:
        self._state = WebSocketServiceStatus.NONE

    def client_received_message(self, message: str) -> None:
        self._messenger.deliver_message(jsonpickle.decode(message))

    def client_received_binary_message(self, message: QByteArray) -> None:
        decompressed_data = zlib.decompress(message)
        self.client_received_message(decompressed_data.decode('utf-8'))
