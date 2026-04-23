from AppCore.DataSource.PlayerStandings.DataSourcePlayerStandingsProtocol import \
    DataSourcePlayerStandingsProtocol
from AppCore.DataSource.PlayerStandings.Events import PlayerStandingsDidUpdate
from AppUI.AppDependenciesInternalProviding import \
    AppDependenciesInternalProviding
from R4UI import Label, RWidget, VerticalBoxLayout
from AppCore.Observation import TransmissionProtocol, TransmissionReceiverProtocol


class PlayerStandingsViewController(RWidget, TransmissionReceiverProtocol):
    def __init__(self,
                 app_dependencies_provider: AppDependenciesInternalProviding):
        super().__init__()
        self._data_source_player_standings_provider = app_dependencies_provider.data_source_player_standings_provider

        app_dependencies_provider.observation_tower.subscribe_multi(self, [PlayerStandingsDidUpdate])

        self._setup_view()

    @property
    def _data_source_player_standing(self) -> DataSourcePlayerStandingsProtocol:
        return self._data_source_player_standings_provider.data_source_player_standing

    def _setup_view(self):
        self._standings_list = VerticalBoxLayout()

        VerticalBoxLayout([
            self._standings_list,
        ]).set_layout_to_widget(self)

        self._data_source_player_standing.retrieve_standings()

    def _sync_ui(self):
        labels = list(map(lambda x: Label(x.name), self._data_source_player_standing.standings))
        self._standings_list.replace_all_widgets(labels)

    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        if type(event) is PlayerStandingsDidUpdate:
            self._sync_ui()