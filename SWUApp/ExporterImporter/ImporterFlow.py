
from typing import List

from PySide6.QtWidgets import QDialog, QTextEdit

from AppCore.DataSource.DataSourceCardSearchClientProtocol import (
    DataSourceCardSearchClientProtocol, DataSourceCardSearchClientProviding,
    DataSourceCardSearchClientSearchResult)
from AppCore.Models import PaginationConfiguration, SearchConfiguration
from R4UI import RComboBox, PushButton, VerticalBoxLayout, HorizontalBoxLayout, RBoldLabel, RHorizontallyExpandingSpacer

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

        self._import_formats = RComboBox(list(map(lambda x: x.format_name, self._importers)))

        VerticalBoxLayout([
            self._text_edit,
            HorizontalBoxLayout([
                RBoldLabel("Format"),
                self._import_formats
            ]).add_spacer(RHorizontallyExpandingSpacer()),
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

# class ImporterSearchClient(DataSourceCardSearchClientProviding, DataSourceCardSearchClientProtocol):

#     def __init__(self,
#                  swu_app_dependencies_provider: SWUAppDependenciesProviding):
#         self._remote_client = SWUDBAPIRemoteClient(swu_app_dependencies_provider)

#     @property
#     def source_display_name(self) -> str:
#         return "swu-db.com"
        
#     def search_with_result(self, 
#                search_configuration: SearchConfiguration,
#                pagination_configuration: PaginationConfiguration) -> DataSourceCardSearchClientSearchResult:
#         # TODO: switch depending on the config
#         return self._remote_client.search_with_result(search_configuration, pagination_configuration)
    
#     @property
#     def search_client(self) -> DataSourceCardSearchClientProtocol:
#         return self
        

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
