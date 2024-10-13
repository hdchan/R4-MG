
from typing import List

from PyQt5.QtWidgets import QPushButton, QSizePolicy, QVBoxLayout, QWidget

from AppCore.Config import Configuration
from AppCore.Observation import ObservationTower
from ..Base import ImagePreviewViewController, SearchTableView


class CardSearchPreviewViewController(QWidget):
    def __init__(self, observation_tower: ObservationTower, configuration: Configuration):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # https://stackoverflow.com/a/19011496
        preview_view = ImagePreviewViewController(observation_tower=observation_tower, 
                                                  configuration=configuration)
        preview_view.delegate = self
        preview_view.setMinimumHeight(300)
        
        self.staging_view = preview_view
        preview_view.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        # lbl2.setMinimumHeight(300);
        layout.addWidget(preview_view)

        flip_button = QPushButton()
        flip_button.setText("Flip (Ctrl+F)")
        flip_button.setEnabled(False)
        flip_button.clicked.connect(self.tapped_flip_button)
        self.flip_button = flip_button
        layout.addWidget(flip_button)

        # Separador = QFrame()
        # Separador.setFrameShape(QFrame.HLine)
        # Separador.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        # Separador.setLineWidth(1)
        # layout.addWidget(Separador)
        
        search_table_view = SearchTableView(observation_tower)
        search_table_view.delegate = self
        self.search_table_view = search_table_view
        layout.addWidget(search_table_view)


    @property
    def delegate(self):
        return self._delegate
    
    @delegate.setter
    def delegate(self, value):
        self._delegate = value
        self.search_table_view.delegate = value
        self.staging_view.delgate = value

    def set_search_focus(self):
        self.search_table_view.set_search_focus()

    def set_item_active(self, index: int):
        self.search_table_view.set_item_active(index)

    def set_image(self, img_alt: str, img_path: str, is_flippable: bool):
        self.staging_view.set_image(img_alt, img_path)
        self.flip_button.setEnabled(is_flippable)

    def update_list(self, result_list: List[str]):
        self.search_table_view.update_list(result_list)

    def tapped_flip_button(self):
        self.delegate.cs_did_tap_flip_button(self)


    