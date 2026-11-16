from typing import Any

from Libraries.Utilities.GeneralWorker import AsyncWorker

from .DataSourceDeckMetaClientProtocol import DataSourceDeckMetaClientProtocol
from .DataSourceDeckMetaProtocol import DataSourceDeckMetaProtocol


class DataSourceDeckMetaDelegate:
    def dsdm_did_retrieve_deck_list_identifiers_ranked(self, ds: 'DataSourceDeckMeta', list: list[str]):
        pass

    def dsdm_did_retrieve_deck_details(self, ds: 'DataSourceDeckMeta', identifier: str, details: dict[str, Any]):
        pass


class DataSourceDeckMeta(DataSourceDeckMetaProtocol):
    def __init__(self, deck_meta_client: DataSourceDeckMetaClientProtocol):
        self._deck_meta_client = deck_meta_client
        self._async_worker = AsyncWorker()
        self.delegate: DataSourceDeckMetaDelegate | None = None

    def retrieve_deck_list_identifiers_ranked(self):
        def completed_with_result(result: list[str]):
            if self.delegate is not None:
                self.delegate.dsdm_did_retrieve_deck_list_identifiers_ranked(
                    self, result)

        def _runnable_fn():
            return self._deck_meta_client.deck_list_identifiers_ranked()

        self._async_worker.run(_runnable_fn, completed_with_result)

    def retrieve_deck_details(self, identifier: str):
        def completed_with_result(result: list[str]):
            if self.delegate is not None:
                self.delegate.dsdm_did_retrieve_deck_list_identifiers_ranked(
                    self, result)

        def _runnable_fn():
            return self._deck_meta_client.deck_details(identifier=identifier)

        self._async_worker.run(_runnable_fn, completed_with_result)
