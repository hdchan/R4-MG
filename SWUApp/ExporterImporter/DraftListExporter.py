from typing import List

from PySide6.QtWidgets import QDialog, QFileDialog

from R4UI import (
        HorizontalBoxLayout,
        PushButton,
        RBoldLabel,
        RComboBox,
        RHorizontallyExpandingSpacer,
        VerticalBoxLayout,
)

from ..ExporterImporter.ExportImportFormattable import ExportFormattable
from ..Models.ParsedDeckList import ParsedDeckList
from ..SWUAppDependenciesProviding import SWUAppDependenciesProviding
from .HandlerProvider import HandlerProvider


class DraftListExporterDialog(QDialog):
        def __init__(self, 
                     exporters: List[ExportFormattable]):
            super().__init__()
            self._exporters = exporters
            
            self._accept_button = PushButton("Export", self.accept) 
            self._export_format = RComboBox(list(map(lambda x: x.format_name, self._exporters)))
            
            VerticalBoxLayout([
                HorizontalBoxLayout([
                    RBoldLabel("Format"),
                    self._export_format
                ]).add_spacer(RHorizontallyExpandingSpacer()),
                HorizontalBoxLayout([
                    PushButton("Cancel", self.reject),
                    self._accept_button
                ])
            ]).set_layout_to_widget(self)
        
        @property
        def _export_format_index(self) -> int:
            return self._export_format.currentIndex()
        
        @property
        def selected_exporter(self) -> ExportFormattable:
            return self._exporters[self._export_format_index]

class DraftListExporter:
    def export_draft_list(self, swu_app_dependencies_provider: SWUAppDependenciesProviding):
        draft_packs = swu_app_dependencies_provider.data_source_draft_list.draft_packs
        parsed_deck_list = ParsedDeckList.from_draft_packs(draft_packs)
        
        if len(parsed_deck_list.first_leader_and_first_base) < 2:
            raise Exception("Please select a leader and a base")
        
        exporters = HandlerProvider(swu_app_dependencies_provider).export_handlers
        
        card_selector = DraftListExporterDialog(exporters)
        result = card_selector.exec()
        if result == QDialog.DialogCode.Rejected:
            return 
        selected_exporter = card_selector.selected_exporter
        
        file_path, ok = QFileDialog.getSaveFileName(None, 
                                                    "Save File", 
                                                    "", 
                                                    f"{selected_exporter.file_format};;All Files (*)")
        
        if not ok:
            return
        
        selected_exporter.export(file_path, parsed_deck_list)