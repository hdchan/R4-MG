
from typing import List

from PyQt5.QtWidgets import QDialog, QTextEdit

from AppCore.DataSource.DataSourceCardSearchClientProtocol import (
    DataSourceCardSearchClientProtocol, DataSourceCardSearchClientProviding,
    DataSourceCardSearchClientSearchCallback)
from AppCore.Models import PaginationConfiguration, SearchConfiguration
from R4UI import ComboBox, PushButton, VerticalBoxLayout, HorizontalBoxLayout, BoldLabel, R4UIHorizontallyExpandingSpacer

from ..swu_db_com.SWUDBAPIRemoteClient import SWUDBAPIRemoteClient
from ..SWUAppDependenciesProviding import SWUAppDependenciesProviding
from .ExportImportFormattable import Importable
from .HandlerProvider import HandlerProvider


class ImporterDialog(QDialog):
    def __init__(self, importers: List[Importable]):
        super().__init__()
        self._importers = importers
        self._text_edit = QTextEdit()
        self._text_edit.setPlaceholderText("Paste deck list")

        self._import_formats = ComboBox(list(map(lambda x: x.format_name, self._importers)))

        VerticalBoxLayout([
            self._text_edit,
            HorizontalBoxLayout([
                BoldLabel("Format"),
                self._import_formats
            ]).add_spacer(R4UIHorizontallyExpandingSpacer()),
            PushButton("Import", self.accept)
        ]).set_layout_to_widget(self)

    @property
    def data_string(self) -> str:
        return self._text_edit.toPlainText()
    
    @property
    def _import_format_index(self) -> int:
        return self._import_formats.currentIndex()

    @property
    def selected_importer(self) -> Importable:
        return self._importers[self._import_format_index]

class ImporterSearchClient(DataSourceCardSearchClientProviding, DataSourceCardSearchClientProtocol):

    def __init__(self,
                 swu_app_dependencies_provider: SWUAppDependenciesProviding):
        self._remote_client = SWUDBAPIRemoteClient(swu_app_dependencies_provider)

    @property
    def source_display_name(self) -> str:
        return "swu-db.com"
        
    def search(self, 
               search_configuration: SearchConfiguration,
               pagination_configuration: PaginationConfiguration,
               callback: DataSourceCardSearchClientSearchCallback) -> None:
        # TODO: switch depending on the config
        self._remote_client.search(search_configuration, pagination_configuration, callback)
    
    @property
    def search_client(self) -> DataSourceCardSearchClientProtocol:
        return self
        

class ImporterFlow:
    def __init__(self, 
                 swu_app_dependencies_provider: SWUAppDependenciesProviding):
        self._swu_app_dependencies_provider = swu_app_dependencies_provider

    def start(self):
        importers = HandlerProvider(self._swu_app_dependencies_provider).import_handlers
        dialog = ImporterDialog(importers)
        result = dialog.exec()
        if result:
            dialog.selected_importer.import_text(dialog.data_string)
