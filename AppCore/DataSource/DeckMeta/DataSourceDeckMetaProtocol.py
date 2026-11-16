class DataSourceDeckMetaProtocol:
    def retrieve_deck_list_identifiers_ranked(self):
        raise Exception

    def retrieve_deck_details(self, identifier: str):
        raise Exception

class DataSourceDeckMetaProviding:
    @property
    def data_source_deck_meta(self) -> DataSourceDeckMetaProtocol:
        raise Exception