from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
                             QWidget, QComboBox)

from AppCore import Configuration, ObservationTower
from AppCore.Observation.Events import SearchEvent, TransmissionProtocol
from AppCore.Models import CardType
from AppUI.UIComponents import ImagePreviewViewController
from typing import List, Optional

# https://stackoverflow.com/a/73498858
# prevent scrolling of the drop down
class MyQComboBox(QComboBox):
    def __init__(self, scrollWidget=None, *args, **kwargs):
        super(MyQComboBox, self).__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, *args, **kwargs):
        if self.hasFocus():
            return QComboBox.wheelEvent(self, *args, **kwargs)

class ImageDeploymentViewController(QWidget):
    def __init__(self, 
                 observation_tower: ObservationTower, 
                 configuration: Configuration, 
                 card_type_list: List[CardType], 
                 selected_card_type: Optional[CardType]):
        super().__init__()
        # self.setFixedHeight(400)
        vertical_layout = QVBoxLayout()
        
        label = QLabel()
        label.setWordWrap(True)
        font = label.font()
        font.setBold(True)
        font.setPointSize(12)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignLeading)
        vertical_layout.addWidget(label)
        self.label = label

        layout = QHBoxLayout()
        layout_widget = QWidget()
        layout_widget.setLayout(layout)
        
        vertical_layout.addWidget(label)
        vertical_layout.addWidget(layout_widget)
        
        first_column_layout = QVBoxLayout()

        stage_button = QPushButton()
        stage_button.setText("Stage")
        stage_button.clicked.connect(self.tapped_staging_button)
        stage_button.setEnabled(False)
        self.stage_button = stage_button
        first_column_layout.addWidget(stage_button)
        
        unstage_button = QPushButton()
        unstage_button.setText("Unstage")
        unstage_button.clicked.connect(self.tapped_unstaging_button)
        unstage_button.setEnabled(False)
        self.unstage_button = unstage_button
        first_column_layout.addWidget(unstage_button)

        card_type_selection = MyQComboBox()
        # card_type_selection.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # card_type_selection.wheelEvent = None
        for i, k in enumerate(card_type_list):
            card_type_selection.addItem(k.value)
            if selected_card_type is not None and k.value == selected_card_type.value:
                card_type_selection.setCurrentIndex(i)
        card_type_selection.currentIndexChanged.connect(self._card_type_selection_changed)
        self.card_type_selection = card_type_selection
        first_column_layout.addWidget(card_type_selection)
        self._card_type_list = card_type_list
        
        context_search_button = QPushButton()
        context_search_button.setText("Context search")
        context_search_button.clicked.connect(self.tapped_context_search_button)
        context_search_button.setEnabled(False)
        self.context_search_button = context_search_button
        self._update_context_search_button_state()
        first_column_layout.addWidget(context_search_button)

        


        first_column_widget = QWidget()
        first_column_widget.setMaximumHeight(150)
        first_column_widget.setLayout(first_column_layout)
        first_column_widget.setFixedWidth(150)
        layout.addWidget(first_column_widget)

        staging_image_view = ImagePreviewViewController(observation_tower, 
                                                        configuration)
        layout.addWidget(staging_image_view, 4)
        self.staging_image_view = staging_image_view

        production_image_view = ImagePreviewViewController(observation_tower, 
                                                           configuration)
        layout.addWidget(production_image_view, 4)
        self.production_image_view = production_image_view

        self.setLayout(vertical_layout)

        self.delegate = None
        
        observation_tower.subscribe(self, SearchEvent)
        
    def set_staging_image(self, img_alt: str, img_path: str):
        self.staging_image_view.set_image(img_alt, img_path)
        self.set_unstage_button_enabled(True)

    def clear_staging_image(self):
        self.staging_image_view.clear_image()
        self.set_unstage_button_enabled(False)

    def set_production_image(self, img_alt: str, img_path: str):
        self.production_image_view.set_image(img_alt, img_path)

    def set_label(self, text: str):
        self.label.setText(text)

    def tapped_staging_button(self):
        self.delegate.id_did_tap_staging_button(self)
        
    def tapped_context_search_button(self):
        self.delegate.id_did_tap_context_search_button(self)

    def set_unstage_button_enabled(self, enabled: bool):
        self.unstage_button.setEnabled(enabled)
        if enabled:
            self.unstage_button.setStyleSheet("background-color : #FA9189")
        else:
            self.unstage_button.setStyleSheet("")

    def set_staging_button_enabled(self, enabled: bool):
        self.stage_button.setEnabled(enabled)
        if enabled:
            self.stage_button.setStyleSheet("background-color : #FFE699")
        else:
            self.stage_button.setStyleSheet("")

    def tapped_unstaging_button(self):
        self.delegate.id_did_tap_unstaging_button(self)
    
    def _update_context_search_button_state(self):
        selected_card_type = self._card_type_list[self.card_type_selection.currentIndex()]
        self.context_search_button.setEnabled(selected_card_type != CardType.UNSPECIFIED)

    def _card_type_selection_changed(self):
        selected_card_type = self._card_type_list[self.card_type_selection.currentIndex()]
        self.delegate.id_did_change_card_type(self, selected_card_type)
        self._update_context_search_button_state()
        
    def handle_observation_tower_event(self, event: TransmissionProtocol):
        if type(event) == SearchEvent:
            if event.event_type == SearchEvent.EventType.STARTED:
                pass
                # self.context_search_button.setEnabled(False)
                # self.card_type_selection.setEnabled(False) # causes unintentional scrolling
            elif event.event_type == SearchEvent.EventType.FINISHED:
                pass
                # self._update_context_search_button_state()
                # self.card_type_selection.setEnabled(True)
