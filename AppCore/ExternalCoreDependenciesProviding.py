from AppCore.DataSource import (
    DataSourceCardSearchClientProviding,
    DataSourceLocallyManagedSets,
)
from AppCore.DataSource.DataSourceLocallyManagedSets import (
    DataSourceLocallyManagedSetsClientProtocol,
)
from AppCore.DataSource.PlayerStandings.DataSourcePlayerStandingsProtocol import (
    DataSourcePlayerStandingsClientProtocol,
)


class ExternalCoreDependenciesProviding:

    @property
    def locally_managed_sets_client(self) -> DataSourceLocallyManagedSetsClientProtocol:
        raise Exception

    # MARK: - Player Standings
    @property
    def player_standings_data_source_client(self) -> DataSourcePlayerStandingsClientProtocol:
        raise Exception

    def data_source_card_search_client_provider(self,
                                                local_managed_sets_data_source: DataSourceLocallyManagedSets) -> DataSourceCardSearchClientProviding:
        raise Exception
