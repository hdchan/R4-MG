from typing import Any


class DataSourceDeckMetaClientProtocol:
    def deck_list_identifiers_ranked(self) -> list[str]:
        return []

    def deck_details(self, identifier: str) -> dict[str, Any]:
        return {}