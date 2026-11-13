

from AppCore.DataSource import (
    DataSourceCardSearchClientProviding,
    DataSourceLocallyManagedSets,
)
from AppCore.DataSource.DataSourceLocallyManagedSets import (
    DataSourceLocallyManagedSetsClientProtocol,
)
from AppCore.DataSource.ImageResourceDeployer import (
    DataSourceImageResourceDeployerProtocol,
)
from AppCore.DataSource.PlayerStandings.DataSourcePlayerStandingsProtocol import (
    DataSourcePlayerStandingsClientProtocol,
)
from AppCore.Models import LocalCardResource, SearchConfiguration
from AppUI.Models import DraftListStyleSheet
from AppUI.Router.Router import Router
from R4UI import RMenuListBuilder, RWidget


class SearchQueryBarViewProviderDelegate:
    def query_text_field_did_update(self, text: str) -> None:
        return


class SearchQueryBarViewProviding(RWidget):
    @property
    def delegate(self) -> SearchQueryBarViewProviderDelegate | None:
        return None

    @property
    def search_configuration(self) -> SearchConfiguration:
        raise Exception

    @property
    def secondary_search_configuration(self) -> SearchConfiguration | None:
        return None

    @property
    def tertiary_search_configuration(self) -> SearchConfiguration | None:
        return None

    def did_receive_configuration(self, search_configuration: SearchConfiguration) -> None:
        return

    def set_search_focus(self) -> None:
        return

    def reset_search(self) -> None:
        return

    def set_enabled(self, is_on: bool) -> None:
        return


class ExternalAppDependenciesProviding:

    @property
    def logo_path(self) -> str:
        return ""

    def hook_developer_menu(self, menu: RMenuListBuilder) -> RMenuListBuilder | None:
        return None

    # MARK: - Card search
    def provide_card_search_query_view(self, delegate: SearchQueryBarViewProviderDelegate | None) -> SearchQueryBarViewProviding | None:
        return None

    # MARK: - Image deployer
    @property
    def card_back_image_path(self) -> str:
        return ""

    @property
    def image_preview_logo_path(self) -> str:
        return ""

    def provide_about_view_controller(self) -> RWidget:
        raise Exception

    def provide_additional_quick_guide(self) -> RWidget | None:
        return None

    # MARK: - Draft List
    def provide_image_deployer_banner_cta(self,
                                          data_source_image_resource_deployer: DataSourceImageResourceDeployerProtocol,
                                          router: Router) -> RWidget | None:
        return None

    @property
    def locally_managed_sets_client(self) -> DataSourceLocallyManagedSetsClientProtocol:
        raise Exception

    def data_source_card_search_client_provider(self,
                                                local_managed_sets_data_source: DataSourceLocallyManagedSets) -> DataSourceCardSearchClientProviding:
        raise Exception

    def provide_draft_list_image_preview_widget(self) -> RWidget:
        raise Exception

    # MARK: - Player Standings
    @property
    def player_standings_data_source_client(self) -> DataSourcePlayerStandingsClientProtocol:
        raise Exception

    # Optional
    def draft_list_item_cell(self,
                             local_card_resource: LocalCardResource,
                             pack_index: int,
                             card_index: int,
                             stylesheet: DraftListStyleSheet,
                             is_presentation: bool) -> RWidget | None:
        return None

    def draft_list_item_header(self,
                               stylesheet: DraftListStyleSheet,
                               text: str) -> RWidget | None:
        return None

    def export_draft_list(self) -> None:
        return None

    def import_draft_list(self) -> None:
        return None

    def draft_resource_list(self,
                            unaggregated_list: list[LocalCardResource],
                            aggregate_list: bool) -> list[LocalCardResource] | None:
        return None
