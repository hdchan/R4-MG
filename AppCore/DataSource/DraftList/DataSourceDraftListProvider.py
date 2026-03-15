from AppCore.Config import ConfigurationManager
from AppCore.Observation import ObservationTower
from AppCore.Observation.Events import DataSourceDraftListProviderStatusUpdatedEvent
from AppCore.Service import DataSerializer

from .DataSourceDraftList import DataSourceDraftList
from .DataSourceDraftListProtocol import (
    DataSourceDraftListProtocol,
    DataSourceDraftListProviding,
    DataSourceDraftListProviderConnectionStatus
)

from typing import Optional
from .DataSourceDraftListWebSocketClientDecorator import DataSourceDraftListWebSocketClientDecorator
from .DataSourceDraftListWebSocketHostDecorator import DataSourceDraftListWebSocketHostDecorator
import socket

class DataSourceDraftListProvider(DataSourceDraftListProviding):
    def __init__(self, 
                 configuration_manager: ConfigurationManager,
                 observation_tower: ObservationTower, 
                 data_serializer: DataSerializer):
        self._observation_tower = observation_tower
        self._draft_list_data_source = DataSourceDraftList(configuration_manager,
                                                           observation_tower, 
                                                           data_serializer)
        self._lazy_host_decorated: Optional[DataSourceDraftListWebSocketHostDecorator] = None
        self._lazy_client_decorated: Optional[DataSourceDraftListWebSocketClientDecorator] = None

        self.__state: DataSourceDraftListProviderConnectionStatus = DataSourceDraftListProviderConnectionStatus.NONE

    @property
    def state(self) -> DataSourceDraftListProviderConnectionStatus:
        return self._state

    @property
    def _state(self) -> DataSourceDraftListProviderConnectionStatus:
        return self.__state

    @_state.setter
    def _state(self, value: DataSourceDraftListProviderConnectionStatus):
        if self.__state != value:
            self.__state = value
            self._observation_tower.notify(DataSourceDraftListProviderStatusUpdatedEvent())

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

    @property
    def draft_list_data_source(self) -> DataSourceDraftListProtocol:
        if self._state == DataSourceDraftListProviderConnectionStatus.IS_HOST:
            return self._host_decorated
        elif self._state == DataSourceDraftListProviderConnectionStatus.IS_CLIENT:
            return self._client_decorated
        return self._draft_list_data_source

    @property
    def _host_decorated(self) -> DataSourceDraftListWebSocketHostDecorator:
        if self._lazy_host_decorated is None:
            controller = DataSourceDraftListWebSocketHostDecorator(self._draft_list_data_source)
            controller.delegate = self
            self._lazy_host_decorated = controller
        return self._lazy_host_decorated

    @property
    def _client_decorated(self) -> DataSourceDraftListWebSocketClientDecorator:
        if self._lazy_client_decorated is None:
            controller = DataSourceDraftListWebSocketClientDecorator(self._draft_list_data_source)
            controller.delegate = self
            self._lazy_client_decorated = controller
        return self._lazy_client_decorated

    def connect_as_host(self):
        self._state = DataSourceDraftListProviderConnectionStatus.IS_HOST
        self._host_decorated.start_server()

    def connect_as_client(self, ip: str, port: Optional[int]):
        self._state = DataSourceDraftListProviderConnectionStatus.IS_CLIENT
        self._client_decorated.connect(ip, port)

    def disconnect(self):
        self._client_decorated.disconnect()
        self._host_decorated.stop_server()

        self._state = DataSourceDraftListProviderConnectionStatus.NONE