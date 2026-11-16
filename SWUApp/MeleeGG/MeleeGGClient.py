from typing import Any

from AppCore.DataSource.DeckMeta.DataSourceDeckMetaClientProtocol import (
    DataSourceDeckMetaClientProtocol,
)
from Libraries.MeleeGGAPI.MeleeGGAPI import MeleeGGAPI


class MeleeGGClient(DataSourceDeckMetaClientProtocol):
    def __init__(self):
        self._api = MeleeGGAPI()

    def deck_list_identifiers_ranked(self) -> list[str]:
        return []

    def deck_details(self, identifier: str) -> dict[str, Any]:
        return {}
