from typing import Any

from .SocketWorker import SocketWorker
from ..Config import ConfigurationManager, Configuration
from AppCore.Observation.Events import SocketRouterUpdatedEvent, SocketIOReceivedCardEvent
from AppCore.Observation import ObservationTower
from AppCore.DataSource import DataSourceCachedHistory
from AppCore.Models import CardResourceProvider

class SocketRouter:
    class Keys:
        JOIN = 'join-as-base'

    def __init__(self, 
                 configuration_manager: ConfigurationManager, 
                 observation_tower: ObservationTower, 
                 data_source_socket_io_history: DataSourceCachedHistory):
        self._configuration_manager = configuration_manager
        self._observation_tower = observation_tower
        self._socket_worker = SocketWorker()
        self._socket_worker.connected.connect(self._on_connected)
        self._socket_worker.disconnected.connect(self._on_disconnected)
        self._socket_worker.error.connect(self._on_error)
        self._socket_worker.add_card.connect(self._on_add_card)
        self._data_source_socket_io_history = data_source_socket_io_history
        # self._is_establishing_connection = False

    @property
    def is_connected_to_socket(self) -> bool:
        return self._socket_worker.is_connected
    
    @property
    def is_establishing_connection(self) -> bool:
        return self.is_connected_to_socket == False

    @property
    def _configuration(self) -> Configuration:
        return self._configuration_manager.configuration

    def connect_if_possible(self):
        remote_url = self._configuration.remote_socket_url
        if remote_url is None:
            print("no socket url")
            return
        self._socket_worker.set_url(remote_url)
        if not self._socket_worker.isRunning():
            self._socket_worker.start()

    def _on_connected(self):
        print("SIO connected")
        self._socket_worker.emit(self.Keys.JOIN, None)
        self._observation_tower.notify(SocketRouterUpdatedEvent(SocketRouterUpdatedEvent.EventType.CONNECTED))

    def _on_disconnected(self):
        print("SIO disconnected")
        self._observation_tower.notify(SocketRouterUpdatedEvent(SocketRouterUpdatedEvent.EventType.DISCONNECTED))

    def _on_error(self, error: str):
        print(f'SIO error: {error}')

    def _on_add_card(self, data: Any):
        print(f'SIO message: {str(data)}')
        self._observation_tower.notify(SocketIOReceivedCardEvent(data))