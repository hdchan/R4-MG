from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
                             QWidget, QComboBox)

from AppCore import Configuration, ObservationTower
from AppCore.Models import CardType
from AppUI.UIComponents import ImagePreviewViewController
from typing import List

class ImageDeploymentViewController(QWidget):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 configuration: Configuration, 
                 card_type_list: List[CardType]):
        super().__init__()

        self.observation_tower = observation_tower

        layout = QHBoxLayout()
        first_column_layout = QVBoxLayout()

        card_type_selection = QComboBox()
        for i in card_type_list:
            card_type_selection.addItem(i.value)
        card_type_selection.currentIndexChanged.connect(self._card_type_selection_changed)
        self.card_type_selection = card_type_selection
        # first_column_layout.addWidget(card_type_selection)
        self._card_type_list = card_type_list

        label = QLabel()
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        first_column_layout.addWidget(label)
        self.label = label

        stage_button = QPushButton()
        stage_button.setText("Stage")
        stage_button.clicked.connect(self.tapped_staging_button)
        stage_button.setEnabled(False)
        self.stage_button = stage_button
        first_column_layout.addWidget(stage_button)
        
        quick_stage_button = QPushButton()
        quick_stage_button.setText("Quick Stage")
        quick_stage_button.clicked.connect(self.tapped_quick_staging_button)
        quick_stage_button.setEnabled(False)
        self.quick_stage_button = quick_stage_button
        # first_column_layout.addWidget(quick_stage_button)

        unstage_button = QPushButton()
        unstage_button.setText("Unstage")
        unstage_button.clicked.connect(self.tapped_unstaging_button)
        unstage_button.setEnabled(False)
        self.unstage_button = unstage_button
        first_column_layout.addWidget(unstage_button)

        first_column_widget = QWidget()
        first_column_widget.setMaximumHeight(150)
        first_column_widget.setLayout(first_column_layout)
        first_column_widget.setFixedWidth(150)
        layout.addWidget(first_column_widget)

        staging_image_view = ImagePreviewViewController(observation_tower=self.observation_tower, 
                                                        configuration=configuration)
        layout.addWidget(staging_image_view, 4)
        self.staging_image_view = staging_image_view

        production_image_view = ImagePreviewViewController(observation_tower=self.observation_tower, 
                                                           configuration=configuration)
        layout.addWidget(production_image_view, 4)
        self.production_image_view = production_image_view

        self.setLayout(layout)

        self.delegate = None
        
    def set_staging_image(self, img_alt: str, img_path: str):
        self.staging_image_view.set_image(img_alt, img_path)
        self.unstage_button.setEnabled(True)

    def clear_staging_image(self):
        self.staging_image_view.clear_image()
        self.unstage_button.setEnabled(False)

    def set_production_image(self, img_alt: str, img_path: str):
        self.production_image_view.set_image(img_alt, img_path)

    def set_label(self, text: str):
        self.label.setText(text)

    def tapped_staging_button(self):
        self.delegate.id_did_tap_staging_button(self)
        
    def tapped_quick_staging_button(self):
        self.delegate.id_did_tap_quick_staging_button(self)

    def set_staging_button_enabled(self, enabled: bool):
        self.stage_button.setEnabled(enabled)

    def tapped_unstaging_button(self):
        self.delegate.id_did_tap_unstaging_button(self)
        
    def _card_type_selection_changed(self):
        selected_card_type = self._card_type_list[self.card_type_selection.currentIndex()]
        self.delegate.id_did_change_card_type(self, selected_card_type)
        
    def mouseReleaseEvent(self, event):
            print("clicked")
