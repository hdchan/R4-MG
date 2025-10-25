

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

from AppUI.Models import DraftListStyleSheet

from ..Assets.AssetProvider import AssetProvider as InternalAssetProvider
from ..Models.SWUTradingCardModelMapper import SWUTradingCardBackedLocalCardResource
from ..Models.CardType import CardType
from R4UI import Label

class DraftListItemCell(QWidget):
    def __init__(self, 
                 stylesheet: DraftListStyleSheet, 
                 card_index: int, 
                 resource: SWUTradingCardBackedLocalCardResource,
                 internal_asset_provider: InternalAssetProvider, 
                 is_presentation: bool):
        super().__init__()
        self._stylesheet = stylesheet
        self._card_index = card_index
        self._trading_card = resource.guaranteed_trading_card
        self._resource = resource
        self._is_presentation = is_presentation
        self._internal_asset_provider = internal_asset_provider
    
        self._setup_view()
    
    def _setup_view(self):
        horizontal_layout = QHBoxLayout()
        # cell_widget = QWidget()
        self.setLayout(horizontal_layout)
        horizontal_layout.setSpacing(self._stylesheet.cell_content_spacing) # needs its own
        horizontal_layout.setContentsMargins(self._stylesheet.cell_padding_left, 
                                            self._stylesheet.cell_padding_top, 
                                            self._stylesheet.cell_padding_right, 
                                            self._stylesheet.cell_padding_bottom)
        
        palette = self.palette()
        cell_style = self._stylesheet.get_modulo_interval_cell_style(self._card_index)
        if cell_style is not None:
            palette.setColor(QPalette.ColorRole.Window, QColor(cell_style.cell_background_color))
        
        self.setLayout(horizontal_layout)
        self.setAutoFillBackground(True)
        self.setPalette(palette)
        
        palette = QPalette()
        if cell_style is not None:
            palette.setColor(QPalette.ColorRole.Base, QColor(cell_style.cell_font_color))
            
            
        label = Label()
        label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        label.setPalette(palette)

        label_text = self._trading_card.name
        if self._is_presentation == False:
            # if self._resource.is_ready == False:
            #     label_text = f"⛔{label_text}"
            if self._resource.guaranteed_trading_card.card_type == CardType.LEADER:
                label_text = f'[{CardType.LEADER.emoji}] {label_text}'
            elif self._resource.guaranteed_trading_card.card_type == CardType.BASE:
                label_text = f'[{CardType.BASE.emoji}] {label_text}'
            elif self._resource.is_sideboard:
                label_text = f'[🚩] {label_text}'
            else:
                label_text = f'{label_text} - {self._resource.guaranteed_trading_card.card_type.value.capitalize()}'

            label_text += f' {self._resource.guaranteed_trading_card.variants_string}'
        label.setText(label_text)
        
        cost_label = Label()
        cost_label.setText(self._trading_card.cost)
        cost_label.setPalette(palette)
        
        custom_font_path = self._stylesheet.cell_font_path
        if custom_font_path is not None:
            font_id = QFontDatabase.addApplicationFont(custom_font_path)
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            custom_font = QFont(font_families[0], self._stylesheet.cell_font_size)
            label.setFont(custom_font)
            cost_label.setFont(custom_font)
        else:
            current_font = label.font()
            current_font.setPointSize(self._stylesheet.cell_font_size)
            label.setFont(current_font)
            cost_label.setFont(current_font)
        
        horizontal_layout.addWidget(label, 1)
        
        SIZE = self._stylesheet.cell_aspect_image_size
        
        image_view = Label()
        pixmap = QPixmap(1, SIZE)
        # Fill the pixmap with a transparent color (alpha value of 0)
        pixmap.fill(QColor(0, 0, 0, 0)) # R, G, B, Alpha
        image_view.setPixmap(pixmap)
        horizontal_layout.addWidget(image_view)
        
        horizontal_layout.addWidget(cost_label)
        
        swu_trading_card = self._resource.guaranteed_trading_card
        
        for a in swu_trading_card.aspects:
            image_path = a.aspect_image_path(self._internal_asset_provider, SIZE <= 50)
            if image_path is not None:
                image = QPixmap()
                image_view = Label()
                image.load(image_path)
                scaled_image = image.scaled(SIZE, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                image_view.setPixmap(scaled_image)
                horizontal_layout.addWidget(image_view)
                