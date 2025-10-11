from PyQt5.QtWidgets import QDialog, QTextEdit
from R4UI import VerticalBoxLayout, HorizontalBoxLayout, PushButton

class ImporterDialog(QDialog):
    def __init__(self):
        super().__init__()

        self._text_edit = QTextEdit()

        VerticalBoxLayout([
            self._text_edit,
            HorizontalBoxLayout([
                PushButton("Import", self.accept)
            ])
        ]).set_layout_to_widget(self)

    @property
    def data_string(self) -> str:
        return self._text_edit.toPlainText()