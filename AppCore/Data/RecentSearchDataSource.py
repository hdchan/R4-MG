from copy import deepcopy
from datetime import datetime

from AppCore.CoreDependencyProviding import CoreDependencyProviding

from ..Observation import *
from ..Observation.Events import SearchEvent


class RecentSearchDataSource(TransmissionReceiverProtocol):
    def __init__(self,
                 core_dependency_providing: CoreDependencyProviding):
        self._observation_tower = core_dependency_providing.observation_tower

        self._search_history: List[SearchEvent] = []

        self._observation_tower.subscribe(self, SearchEvent)

    

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) == SearchEvent:
            print(event)
