
from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QWidget
from AppUI.Models import DraftListStyleSheet
from R4UI import VerticalBoxLayout, Label
from AppCore.Utilities import FontUtilities

class DraftListItemHeader(QWidget):
    def __init__(self, 
                 stylesheet: DraftListStyleSheet, 
                 text: str):
        super().__init__()
        self._stylesheet = stylesheet
        self._text = text
        self._setup_view()
        
    def _setup_view(self):
        horizontal_layout = QHBoxLayout()
        cell_widget = QWidget()
        cell_widget.setLayout(horizontal_layout)
        
        horizontal_layout.setSpacing(self._stylesheet.cell_header_spacing) # needs its own
        horizontal_layout.setContentsMargins(self._stylesheet.cell_header_padding_left, 
                                            self._stylesheet.cell_header_padding_top, 
                                            self._stylesheet.cell_header_padding_right, 
                                            self._stylesheet.cell_header_padding_bottom)
        
        palette = cell_widget.palette()
        
        palette.setColor(QPalette.ColorRole.Window, QColor(self._stylesheet.cell_header_background_color))
        
        cell_widget.setLayout(horizontal_layout)
        cell_widget.setAutoFillBackground(True)
        cell_widget.setPalette(palette)
            
            
        label = Label()
        label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        label.setText(self._text)
        
        FontUtilities.apply_font_style(label,
                                           self._stylesheet.cell_header_font_path,
                                           self._stylesheet.cell_header_font_size,
                                           self._stylesheet.cell_header_font_color)
        
        horizontal_layout.addWidget(label, 1)
        
        # container_widget = QWidget()
        VerticalBoxLayout([
            cell_widget
        ]).set_uniform_content_margins(0).set_layout_to_widget(self)
        self.setContentsMargins(0, 0, 0, self._stylesheet.cell_header_spacing)