
from PyQt5.QtGui import QColor, QFont, QFontDatabase, QPalette
from PyQt5.QtWidgets import QHBoxLayout, QSizePolicy, QWidget
from AppUI.Models import DraftListStyleSheet
from R4UI import VerticalBoxLayout, Label

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
        
        palette.setColor(QPalette.ColorRole.Background, QColor(self._stylesheet.cell_header_background_color))
        
        cell_widget.setLayout(horizontal_layout)
        cell_widget.setAutoFillBackground(True)
        cell_widget.setPalette(palette)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Foreground, QColor(self._stylesheet.cell_header_font_color))
            
            
        label = Label()
        label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        label.setPalette(palette)
        label.setText(self._text)
        
        custom_font_path = self._stylesheet.cell_header_font_path
        if custom_font_path is not None:
            font_id = QFontDatabase.addApplicationFont(custom_font_path)
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            custom_font = QFont(font_families[0], self._stylesheet.cell_header_font_size)
            label.setFont(custom_font)
        else:
            current_font = label.font()
            current_font.setPointSize(self._stylesheet.cell_header_font_size)
            label.setFont(current_font)
        
        horizontal_layout.addWidget(label, 1)
        
        # container_widget = QWidget()
        VerticalBoxLayout([
            cell_widget
        ]).set_uniform_content_margins(0).set_layout_to_widget(self)
        self.setContentsMargins(0, 0, 0, self._stylesheet.cell_header_spacing)